import json
import os
from sqlalchemy.orm import Session
from src.qcc.db.session import SessionLocal
from src.qcc.db.models import Course, Module, Lesson, ContentBlock, Quiz, User, UserRole
from src.qcc.auth.password import hash_password

def get_or_create_admin(db: Session):
    admin = db.query(User).filter(User.email == "admin@qcc.io").first()
    if not admin:
        admin = User(
            email="admin@qcc.io",
            hashed_password=hash_password("admin123"),
            full_name="Admin",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Admin user created.")
    return admin

def import_course_from_json(filepath: str):
    db = SessionLocal()
    try:
        admin = get_or_create_admin(db)

        with open(filepath, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        for course_data in data["courses"]:
            # Check if course already exists
            existing = db.query(Course).filter(Course.title == course_data["title"]).first()
            if existing:
                print(f"Course '{course_data['title']}' already exists. Skipping.")
                continue

            # Create course
            course = Course(
                title=course_data["title"],
                description=course_data.get("description", ""),
                is_published=course_data.get("is_published", True),
                instructor_id=admin.id
            )
            db.add(course)
            db.flush()

            modules = course_data.get("modules", [])
            for mod_data in modules:
                module = Module(
                    course_id=course.id,
                    title=mod_data["title"],
                    description=mod_data.get("description", ""),
                    order=mod_data.get("order", 0)
                )
                db.add(module)
                db.flush()

                lessons = mod_data.get("lessons", [])
                for lesson_data in lessons:
                    lesson = Lesson(
                        module_id=module.id,
                        title=lesson_data["title"],
                        description=lesson_data.get("description", ""),
                        order=lesson_data.get("order", 0),
                        is_published=lesson_data.get("is_published", True)
                    )
                    db.add(lesson)
                    db.flush()

                    # Content blocks
                    blocks = lesson_data.get("content_blocks", [])
                    for block_data in blocks:
                        block = ContentBlock(
                            lesson_id=lesson.id,
                            content_type=block_data["content_type"],
                            order=block_data.get("order", 0),
                            data=block_data["data"]
                        )
                        db.add(block)

                    # Quiz (if present)
                    quiz_data = lesson_data.get("quiz")
                    if quiz_data:
                        quiz = Quiz(
                            lesson_id=lesson.id,
                            title=quiz_data.get("title", "Quiz"),
                            questions=quiz_data["questions"]
                        )
                        db.add(quiz)

            db.commit()
            print(f"Course '{course.title}' imported successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import_course_from_json("course_data.json")

