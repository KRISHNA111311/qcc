from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum

# ---- ContentBlock schemas ----
class ContentType(str, Enum):
    TEXT = "text"
    VIDEO = "video"
    QUIZ = "quiz"
    CODING = "coding"
    CIRCUIT = "circuit"

class ContentBlockBase(BaseModel):
    content_type: ContentType
    order: int = 0
    data: Dict[str, Any]  # stores text, video URL, quiz ref, circuit template, etc.

class ContentBlockCreate(ContentBlockBase):
    lesson_id: int   # added foreign key

class ContentBlockUpdate(BaseModel):
    content_type: Optional[ContentType] = None
    order: Optional[int] = None
    data: Optional[Dict[str, Any]] = None

class ContentBlockResponse(ContentBlockBase):
    id: int
    lesson_id: int

    class Config:
        from_attributes = True

# ---- Lesson schemas ----
class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int = 0
    is_published: bool = False

class LessonCreate(LessonBase):
    module_id: int   # added foreign key

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_published: Optional[bool] = None

class LessonResponse(LessonBase):
    id: int
    module_id: int
    content_blocks: List[ContentBlockResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ---- Module schemas ----
class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int = 0

class ModuleCreate(ModuleBase):
    course_id: int   # added foreign key

class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None

class ModuleResponse(ModuleBase):
    id: int
    course_id: int
    lessons: List[LessonResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ---- Course schemas ----
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_published: bool = False

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None

class CourseResponse(CourseBase):
    id: int
    instructor_id: int
    modules: List[ModuleResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ---- Enrollment schemas ----
class EnrollRequest(BaseModel):
    course_id: int