import json
from sqlalchemy.orm import Session
from .session import SessionLocal
from .models import Course, Module, Lesson, ContentBlock, User, UserRole
from ..auth.password import hash_password
from datetime import datetime

def seed_database():
    db = SessionLocal()
    try:
        # Create admin user if not exists
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

        # Seed courses
        courses_data = [
            {
                "title": "Introduction to Quantum Computing",
                "description": "Learn the fundamentals of quantum computing, qubits, superposition, and entanglement.",
                "is_published": True,
                "instructor_id": admin.id,
                "modules": [
                    {
                        "title": "Qubits",
                        "description": "Understanding the basic unit of quantum information.",
                        "order": 1,
                        "lessons": [
                            {
                                "title": "What is a Qubit?",
                                "description": "A two-state quantum system.",
                                "order": 1,
                                "is_published": True,
                                "content_blocks": [
                                    {
                                        "content_type": "text",
                                        "order": 1,
                                        "data": {"text": "A qubit is the fundamental unit of quantum information. Unlike a classical bit which is either 0 or 1, a qubit can be in a superposition of both states simultaneously."}
                                    },
                                    {
                                        "content_type": "circuit",
                                        "order": 2,
                                        "data": {"qasm_d": "1#100"}  # simple circuit with measure all
                                    }
                                ]
                            },
                            {
                                "title": "Bloch Sphere",
                                "description": "Geometric representation of a qubit.",
                                "order": 2,
                                "is_published": True,
                                "content_blocks": [
                                    {
                                        "content_type": "text",
                                        "order": 1,
                                        "data": {"text": "The Bloch sphere provides a visual representation of a qubit's state as a point on a sphere."}
                                    }
                                ]
                            },
                            {
                                "title": "Quantum States and Dirac Notation",
                                "description": "Mathematical notation for quantum states.",
                                "order": 3,
                                "is_published": True,
                                "content_blocks": [
                                    {
                                        "content_type": "text",
                                        "order": 1,
                                        "data": {"text": "Quantum states are represented using Dirac notation: |0⟩, |1⟩, and superpositions like α|0⟩ + β|1⟩."}
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Superposition",
                        "description": "Creating and manipulating superposition states.",
                        "order": 2,
                        "lessons": [
                            {
                                "title": "The Hadamard Gate",
                                "description": "Creating superposition with H gate.",
                                "order": 1,
                                "is_published": True,
                                "content_blocks": [
                                    {
                                        "content_type": "text",
                                        "order": 1,
                                        "data": {"text": "The Hadamard gate (H) transforms |0⟩ to (|0⟩+|1⟩)/√2 and |1⟩ to (|0⟩-|1⟩)/√2."}
                                    },
                                    {
                                        "content_type": "circuit",
                                        "order": 2,
                                        "data": {"qasm_d": "1#1#00"}  # H on qubit 0
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Quantum Algorithms",
                "description": "Explore famous quantum algorithms like Grover and Shor.",
                "is_published": True,
                "instructor_id": admin.id,
                "modules": [
                    {
                        "title": "Grover's Algorithm",
                        "description": "Searching an unsorted database quadratically faster.",
                        "order": 1,
                        "lessons": [
                            {
                                "title": "The Oracle",
                                "description": "Marking the target state.",
                                "order": 1,
                                "is_published": True,
                                "content_blocks": [
                                    {
                                        "content_type": "text",
                                        "order": 1,
                                        "data": {"text": "The oracle marks the target state by flipping its phase."}
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]

        for course_data in courses_data:
            # Check if course already exists by title
            existing_course = db.query(Course).filter(Course.title == course_data["title"]).first()
            if existing_course:
                print(f"Course '{course_data['title']}' already exists. Skipping.")
                continue

            modules_data = course_data.pop("modules")
            course = Course(**course_data)
            db.add(course)
            db.flush()  # to get course.id

            for module_data in modules_data:
                lessons_data = module_data.pop("lessons")
                module = Module(**module_data, course_id=course.id)
                db.add(module)
                db.flush()

                for lesson_data in lessons_data:
                    content_blocks_data = lesson_data.pop("content_blocks")
                    lesson = Lesson(**lesson_data, module_id=module.id)
                    db.add(lesson)
                    db.flush()

                    for block_data in content_blocks_data:
                        block = ContentBlock(**block_data, lesson_id=lesson.id)
                        db.add(block)

            db.commit()
            print(f"Course '{course.title}' seeded with {len(modules_data)} modules.")

        print("Database seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
