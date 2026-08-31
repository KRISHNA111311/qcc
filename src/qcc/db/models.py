from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON, Enum,
    Table, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# ---- Enums ----
class UserRole(str, enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"

class ContentType(str, enum.Enum):
    TEXT = "text"
    VIDEO = "video"
    QUIZ = "quiz"
    CODING = "coding"
    CIRCUIT = "circuit"

class ChallengeType(str, enum.Enum):
    QUIZ = "quiz"
    CODING = "coding"

# ---- Association tables ----
# Many-to-many: Course <-> User (enrollment)
course_students = Table(
    "course_students",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("enrolled_at", DateTime, default=datetime.utcnow),
)

# ---- User Model ----
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    courses_teaching = relationship("Course", back_populates="instructor")
    courses_enrolled = relationship("Course", secondary=course_students, back_populates="students")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    challenge_attempts = relationship("CodingChallengeAttempt", back_populates="user", cascade="all, delete-orphan")

# ---- Course Model ----
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    instructor = relationship("User", back_populates="courses_teaching")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    students = relationship("User", secondary=course_students, back_populates="courses_enrolled")

# ---- Module Model ----
class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")

# ---- Lesson Model ----
class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    module = relationship("Module", back_populates="lessons")
    content_blocks = relationship("ContentBlock", back_populates="lesson", cascade="all, delete-orphan")
    quiz = relationship("Quiz", back_populates="lesson", uselist=False, cascade="all, delete-orphan")

# ---- ContentBlock Model (supports multiple types) ----
class ContentBlock(Base):
    __tablename__ = "content_blocks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    order = Column(Integer, default=0)
    data = Column(JSON, nullable=False)  # stores e.g., text, video URL, quiz ref, circuit template

    # Relationships
    lesson = relationship("Lesson", back_populates="content_blocks")

# ---- Quiz Model (for quizzes embedded in lessons) ----
class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, unique=True)
    title = Column(String(255), nullable=True)
    questions = Column(JSON, nullable=False)  # list of {question, options, correct_index}

    # Relationships
    lesson = relationship("Lesson", back_populates="quiz")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

# ---- QuizAttempt Model ----
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    answers = Column(JSON, nullable=False)   # list of chosen indices
    score = Column(Float, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")

# ---- CodingChallenge Model (standalone) ----
class CodingChallenge(Base):
    __tablename__ = "coding_challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    starter_code = Column(Text, nullable=True)      # e.g., QASM-D template
    expected_output = Column(JSON, nullable=False)  # e.g., {"counts": {...}}
    test_cases = Column(JSON, nullable=True)
    difficulty = Column(String(50), default="intermediate")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    attempts = relationship("CodingChallengeAttempt", back_populates="challenge", cascade="all, delete-orphan")

# ---- CodingChallengeAttempt Model ----
class CodingChallengeAttempt(Base):
    __tablename__ = "coding_challenge_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False)
    submitted_code = Column(Text, nullable=False)   # QASM-D or actual code
    passed = Column(Boolean, nullable=True)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="challenge_attempts")
    challenge = relationship("CodingChallenge", back_populates="attempts")

# ---- UserProgress (tracking lesson completion) ----
class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress")
    # lesson relationship (optional)
    # We'll add a direct relationship to Lesson if needed

    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='uq_user_lesson'),
    )