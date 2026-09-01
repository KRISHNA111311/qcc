import json
from sqlalchemy.orm import Session
from .session import SessionLocal
from .models import Course, Module, Lesson, ContentBlock, User, UserRole, Quiz
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

        # Helper to get or create a course
        def get_or_create_course(title, description, is_published=True):
            course = db.query(Course).filter(Course.title == title).first()
            if course:
                print(f"Course '{title}' already exists. Skipping.")
                return course
            course = Course(
                title=title,
                description=description,
                is_published=is_published,
                instructor_id=admin.id
            )
            db.add(course)
            db.flush()
            return course

        # Helper to add modules, lessons, content blocks
        def add_module(course, title, description, order, lessons_data):
            module = Module(
                course_id=course.id,
                title=title,
                description=description,
                order=order
            )
            db.add(module)
            db.flush()
            for lesson_data in lessons_data:
                add_lesson(module, lesson_data)
            return module

        def add_lesson(module, data):
            lesson = Lesson(
                module_id=module.id,
                title=data["title"],
                description=data.get("description", ""),
                order=data.get("order", 0),
                is_published=data.get("is_published", True)
            )
            db.add(lesson)
            db.flush()
            # Add content blocks
            for block_data in data.get("content_blocks", []):
                block = ContentBlock(
                    lesson_id=lesson.id,
                    content_type=block_data["content_type"],
                    order=block_data.get("order", 0),
                    data=block_data["data"]
                )
                db.add(block)
            # Add quiz if present
            if "quiz" in data:
                quiz = Quiz(
                    lesson_id=lesson.id,
                    title=data["quiz"].get("title", "Quiz"),
                    questions=data["quiz"]["questions"]
                )
                db.add(quiz)
            return lesson

        # ================================================================
        # COURSE 1: Introduction to Quantum Computing
        # ================================================================
        course1 = get_or_create_course(
            "Introduction to Quantum Computing",
            "Learn the fundamentals of quantum computing, qubits, superposition, and entanglement."
        )
        if course1.id:
            # Module 1: Qubits
            add_module(course1, "Qubits",
                "Understanding the basic unit of quantum information.", 1,
                [
                    {
                        "title": "What is a Qubit?",
                        "description": "A two-state quantum system.",
                        "order": 1,
                        "content_blocks": [
                            {
                                "content_type": "text",
                                "order": 1,
                                "data": {
                                    "text": "A qubit is the fundamental unit of quantum information. Unlike a classical bit which is either 0 or 1, a qubit can be in a superposition of both states simultaneously.\n\nMathematically, a qubit state is written as |ψ⟩ = α|0⟩ + β|1⟩, where |α|² + |β|² = 1."
                                }
                            },
                            {
                                "content_type": "circuit",
                                "order": 2,
                                "data": {"qasm_d": "1#100"}
                            }
                        ],
                        "quiz": {
                            "title": "Qubit Fundamentals",
                            "questions": [
                                {
                                    "question": "What is a qubit?",
                                    "options": ["A two-state quantum system", "A classical bit", "A quantum gate", "A measurement device"],
                                    "correct": 0,
                                    "explanation": "A qubit is a two-state quantum system that can exist in superposition."
                                },
                                {
                                    "question": "Which notation is used for quantum states?",
                                    "options": ["Bra-ket", "Dirac notation", "Both A and B", "None of the above"],
                                    "correct": 2,
                                    "explanation": "Quantum states are represented using Dirac notation, also called bra-ket notation."
                                }
                            ]
                        }
                    },
                    {
                        "title": "Bloch Sphere",
                        "description": "Geometric representation of a qubit.",
                        "order": 2,
                        "content_blocks": [
                            {
                                "content_type": "text",
                                "order": 1,
                                "data": {
                                    "text": "The Bloch sphere provides a visual representation of a qubit's state as a point on a sphere. The north pole is |0⟩, south pole is |1⟩, and points on the equator represent superpositions."
                                }
                            },
                            {
                                "content_type": "circuit",
                                "order": 2,
                                "data": {"qasm_d": "1#1#00"}  # H on qubit 0
                            }
                        ]
                    },
                    {
                        "title": "Quantum States and Dirac Notation",
                        "description": "Mathematical notation for quantum states.",
                        "order": 3,
                        "content_blocks": [
                            {
                                "content_type": "text",
                                "order": 1,
                                "data": {
                                    "text": "Quantum states are represented using Dirac notation: |0⟩, |1⟩, and superpositions like α|0⟩ + β|1⟩. The inner product ⟨ψ|φ⟩ gives the probability amplitude."
                                }
                            }
                        ]
                    }
                ]
            )

            # Module 2: Superposition
            add_module(course1, "Superposition",
                "Creating and manipulating superposition states.", 2,
                [
                    {
                        "title": "The Hadamard Gate",
                        "description": "Creating superposition with H gate.",
                        "order": 1,
                        "content_blocks": [
                            {
                                "content_type": "text",
                                "order": 1,
                                "data": {
                                    "text": "The Hadamard gate (H) transforms |0⟩ to (|0⟩+|1⟩)/√2 and |1⟩ to (|0⟩-|1⟩)/√2. It creates a superposition of equal probability."
                                }
                            },
                            {
                                "content_type": "circuit",
                                "order": 2,
                                "data": {"qasm_d": "1#1#00"}
                            }
                        ],
                        "quiz": {
                            "title": "Superposition Concepts",
                            "questions": [
                                {
                                    "question": "What does the Hadamard gate do to |0⟩?",
                                    "options": ["Leaves it unchanged", "Creates superposition", "Flips it to |1⟩", "Measures it"],
                                    "correct": 1,
                                    "explanation": "H|0⟩ = (|0⟩+|1⟩)/√2, creating a superposition."
                                }
                            ]
                        }
                    },
                    {
                        "title": "Creating Superposition",
                        "description": "Using rotation gates to create arbitrary superposition.",
                        "order": 2,
                        "content_blocks": [
                            {
                                "content_type": "text",
                                "order": 1,
                                "data": {
                                    "text": "Rotation gates RX, RY, RZ allow you to create any superposition by adjusting angles. For example, RY(θ) rotates the state around the Y-axis."
                                }
                            },
                            {
                                "content_type": "circuit",
                                "order": 2,
                                "data": {"qasm_d": "1#9078#00"}  # RY(1.2) on qubit 0
                            }
                        ]
                    }
                ]
            )

            # Module 3: Entanglement
            add_module(course1, "Entanglement",
                "Understanding quantum entanglement and Bell states.", 3,
                [
                    {
                        "title": "Bell States",
                        "description": "Creating entangled pairs.",
                        "order": 1,
                        "content_blocks": [
                            {
                                "content_type": "text",
                                "order": 1,
                                "data": {
                                    "text": "Bell states are maximally entangled states of two qubits. The state |Φ+⟩ = (|00⟩+|11⟩)/√2 is created by applying H on qubit 0 then CNOT(0,1)."
                                }
                            },
                            {
                                "content_type": "circuit",
                                "order": 2,
                                "data": {"qasm_d": "2#11#212#00"}
                            }
                        ],
                        "quiz": {
                            "title": "Entanglement Concepts",
                            "questions": [
                                {
                                    "question": "Which gate creates entanglement?",
                                    "options": ["Hadamard", "CNOT", "Pauli-X", "Phase shift"],
                                    "correct": 1,
                                    "explanation": "CNOT is the entangling gate; it creates correlation between qubits."
                                }
                            ]
                        }
                    },
                    {
                        "title": "Entangled Measurements",
                        "description": "Measuring one qubit affects the other.",
                        "order": 2,
                        "content_blocks": [
                            {
                                "content_type": "text",
                                "order": 1,
                                "data": {
                                    "text": "In a Bell state, measuring one qubit instantly determines the other qubit's state, regardless of distance. This is a key feature of quantum entanglement."
                                }
                            },
                            {
                                "content_type": "circuit",
                                "order": 2,
                                "data": {"qasm_d": "2#11#212#A1#A2#00"}  # Bell with measurements
                            }
                        ]
                    }
                ]
            )

        # ================================================================
        # COURSE 2: Quantum Algorithms
        # ================================================================
        course2 = get_or_create_course(
            "Quantum Algorithms",
            "Explore famous quantum algorithms like Grover and Shor."
        )
        if course2.id:
            # Module 1: Grover's Algorithm
            add_module(course2, "Grover's Algorithm",
                "Searching an unsorted database quadratically faster.", 1,
                [
                    {
                        "title": "The Oracle",
                        "description": "Marking the target state.",
                        "order": 1,
                        "content_blocks": [
                            {
                                "content_type": "text",
                                "order": 1,
                                "data": {
                                    "text": "The oracle flips the phase of the target state. It's a black box that recognizes the solution."
                                }
                            },
                            {
                                "content_type": "circuit",
                                "order": 2,
                                "data": {"qasm_d": "2#11#212#12#00"}  # Simple oracle for |11⟩
                            }
                        ]
                    },
                    {
                        "title": "Amplitude Amplification",
                        "description": "The Grover diffusion operator.",
                        "order": 2,
                        "content_blocks": [
                            {
                                "content_type": "text",
                                "order": 1,
                                "data": {
                                    "text": "After the oracle, the Grover diffusion operator amplifies the probability of the marked state. Repeating the oracle+diffusion increases the success probability."
                                }
                            }
                        ],
                        "quiz": {
                            "title": "Grover's Algorithm",
                            "questions": [
                                {
                                    "question": "What is the purpose of the oracle?",
                                    "options": ["To mark the target state", "To measure the qubits", "To create entanglement", "To apply a Hadamard"],
                                    "correct": 0,
                                    "explanation": "The oracle marks the target state by flipping its phase."
                                }
                            ]
                        }
                    }
                ]
            )

        db.commit()
        print("✅ Database seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
