from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from ..db import get_db
from ..db.models import User, UserProgress, Lesson, Course, Module, UserRole
from ..auth.dependencies import get_current_user
from ..schemas import LessonResponse, CourseResponse  # reuse schemas

router = APIRouter(prefix="/api/progress", tags=["progress"])

# ============ Mark Lesson as Complete ============
@router.post("/lesson/{lesson_id}/complete")
def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if already completed
    existing = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.lesson_id == lesson_id
    ).first()
    if existing:
        # If already completed, just return success (or update timestamp)
        existing.last_accessed = datetime.utcnow()
        db.commit()
        return {"message": "Lesson already completed", "completed_at": existing.completed_at}
    
    # Mark as completed
    progress = UserProgress(
        user_id=current_user.id,
        lesson_id=lesson_id,
        completed=True,
        completed_at=datetime.utcnow(),
        last_accessed=datetime.utcnow()
    )
    db.add(progress)
    db.commit()
    return {"message": "Lesson marked as completed", "completed_at": progress.completed_at}

# ============ Get Student Dashboard ============
@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only for students (or any user)
    # Get all courses the user is enrolled in
    enrolled_courses = current_user.courses_enrolled
    
    dashboard = []
    for course in enrolled_courses:
        # Count total lessons in the course (published)
        total_lessons = db.query(Lesson).join(Module).filter(
            Module.course_id == course.id,
            Lesson.is_published == True
        ).count()
        
        # Count completed lessons by this user for this course
        completed_lessons = db.query(UserProgress).join(Lesson).join(Module).filter(
            UserProgress.user_id == current_user.id,
            Module.course_id == course.id,
            UserProgress.completed == True
        ).count()
        
        progress_pct = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        dashboard.append({
            "course_id": course.id,
            "course_title": course.title,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": round(progress_pct, 1)
        })
    
    return dashboard

# ============ Instructor Dashboard: Course Statistics ============
@router.get("/instructor/course/{course_id}/stats")
def get_course_stats(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user is instructor/admin of this course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only instructors/admins can view stats")
    if current_user.id != course.instructor_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not your course")
    
    # Enrolled students
    enrolled_students = course.students  # many-to-many relationship
    total_students = len(enrolled_students)
    
    # Total lessons in the course
    total_lessons = db.query(Lesson).join(Module).filter(
        Module.course_id == course_id,
        Lesson.is_published == True
    ).count()
    
    # For each student, get progress
    student_progress = []
    for student in enrolled_students:
        completed = db.query(UserProgress).join(Lesson).join(Module).filter(
            UserProgress.user_id == student.id,
            Module.course_id == course_id,
            UserProgress.completed == True
        ).count()
        progress_pct = (completed / total_lessons * 100) if total_lessons > 0 else 0
        student_progress.append({
            "student_id": student.id,
            "student_email": student.email,
            "completed_lessons": completed,
            "progress_percentage": round(progress_pct, 1)
        })
    
    # Overall stats
    if total_students > 0:
        avg_progress = sum(s["progress_percentage"] for s in student_progress) / total_students
        completed_all = sum(1 for s in student_progress if s["progress_percentage"] == 100)
    else:
        avg_progress = 0
        completed_all = 0
    
    return {
        "course_id": course_id,
        "course_title": course.title,
        "total_students": total_students,
        "total_lessons": total_lessons,
        "average_progress": round(avg_progress, 1),
        "students_completed_all": completed_all,
        "student_details": student_progress
    }