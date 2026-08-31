from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..db import get_db
from ..db.models import User, Course, Module, Lesson, ContentBlock, UserRole, course_students
from ..auth.dependencies import get_current_user, get_current_active_admin
from ..schemas import (
    CourseCreate, CourseUpdate, CourseResponse,
    ModuleCreate, ModuleUpdate, ModuleResponse,
    LessonCreate, LessonUpdate, LessonResponse,
    ContentBlockCreate, ContentBlockUpdate, ContentBlockResponse,
    EnrollRequest
)
from datetime import datetime

router = APIRouter(prefix="/api/content", tags=["content"])

# ============ COURSE ENDPOINTS ============
@router.get("/courses", response_model=List[CourseResponse])
def list_courses(
    published_only: bool = Query(True, description="Only show published courses"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # authenticated
):
    query = db.query(Course)
    if published_only:
        query = query.filter(Course.is_published == True)
    # Optionally, we can filter by enrollment later
    courses = query.options(joinedload(Course.modules).joinedload(Module.lessons).joinedload(Lesson.content_blocks)).all()
    return courses

@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).options(
        joinedload(Course.modules).joinedload(Module.lessons).joinedload(Lesson.content_blocks)
    ).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_published and current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Course not published")
    return course

@router.post("/courses", response_model=CourseResponse, status_code=201)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)  # only admin/instructor
):
    # Only admins or instructors can create; we require admin for now, but can relax to instructor.
    # Actually we should allow any instructor, but we'll use admin for simplicity; we can extend.
    db_course = Course(
        title=course.title,
        description=course.description,
        is_published=course.is_published,
        instructor_id=current_user.id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    # Only instructor who owns it or admin can update
    if current_user.id != db_course.instructor_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    for field, value in course_update.dict(exclude_unset=True).items():
        setattr(db_course, field, value)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/courses/{course_id}", status_code=204)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.id != db_course.instructor_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db.delete(db_course)
    db.commit()
    return {"ok": True}

# ============ MODULE ENDPOINTS ============
@router.get("/modules", response_model=List[ModuleResponse])
def list_modules(
    course_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Module).options(joinedload(Module.lessons).joinedload(Lesson.content_blocks))
    if course_id:
        query = query.filter(Module.course_id == course_id)
    modules = query.all()
    return modules

@router.post("/modules", response_model=ModuleResponse, status_code=201)
def create_module(
    module: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # Verify course exists and user owns it or is admin
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.id != course.instructor_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_module = Module(**module.dict())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

# Similar for update and delete modules (omitted for brevity – can be added similarly)

# ============ LESSON ENDPOINTS ============
@router.post("/lessons", response_model=LessonResponse, status_code=201)
def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # Verify module exists and course ownership
    module = db.query(Module).filter(Module.id == lesson.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if not course or (current_user.id != course.instructor_id and current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_lesson = Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

# GET lessons by module, GET single lesson, etc.

# ============ CONTENT BLOCK ENDPOINTS ============
@router.post("/content-blocks", response_model=ContentBlockResponse, status_code=201)
def create_content_block(
    block: ContentBlockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # Verify lesson exists and ownership
    lesson = db.query(Lesson).filter(Lesson.id == block.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    module = db.query(Module).filter(Module.id == lesson.module_id).first()
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if not course or (current_user.id != course.instructor_id and current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_block = ContentBlock(**block.dict())
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block

# PUT, DELETE for content blocks similarly

# ============ ENROLLMENT ENDPOINTS ============
@router.post("/enroll", status_code=200)
def enroll_course(
    enroll: EnrollRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == enroll.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_published:
        raise HTTPException(status_code=400, detail="Course not published")
    # Check if already enrolled
    if course in current_user.courses_enrolled:
        raise HTTPException(status_code=400, detail="Already enrolled")
    current_user.courses_enrolled.append(course)
    db.commit()
    return {"message": "Enrolled successfully"}

@router.delete("/enroll/{course_id}", status_code=204)
def unenroll_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course not in current_user.courses_enrolled:
        raise HTTPException(status_code=400, detail="Not enrolled")
    current_user.courses_enrolled.remove(course)
    db.commit()
    return {"ok": True}

# ============ PROGRESS TRACKING (basic) ============
# We'll add progress endpoints later in Phase 4