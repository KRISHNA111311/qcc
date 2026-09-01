import json
import os
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types
import traceback

from ..config import get_settings
from ..core.models import CircuitAST


def serialize_circuit(ast: CircuitAST) -> Dict[str, Any]:
    """Convert CircuitAST to a JSON-serializable dict for the AI prompt."""
    return {
        "num_qubits": ast.num_qubits,
        "num_classical": ast.num_classical,
        "operations": [
            {
                "type": g.type.value,
                "qubits": g.qubits,
                "params": g.params
            }
            for g in ast.operations
        ],
        "depth": len(ast.operations)  # simplified
    }


def build_prompt(
    circuit_data: Dict[str, Any],
    errors: List[Dict[str, Any]],
    user_query: str = ""
) -> str:
    prompt = f"""
You are a quantum computing tutor. Analyze the following quantum circuit and answer the student's question.

**Circuit:**
```json
{json.dumps(circuit_data, indent=2)}
```

Detected errors/warnings:
{json.dumps(errors, indent=2) if errors else "None"}

Student question: {user_query if user_query else "Explain this circuit in simple terms."}

Provide:

A clear explanation of what the circuit does.

If there are errors, explain each one and suggest fixes.

Highlight key quantum concepts involved.

Any tips for improvement.

Keep it educational and concise (max 300 words).
"""
    return prompt


def get_ai_response(prompt: str) -> str:
    """Call Gemini with fallback across multiple API keys."""
    settings = get_settings()
    keys = settings.GEMINI_API_KEYS

    if not keys:
        raise RuntimeError(
            "No Gemini API keys configured. Set GEMINI_API_KEY1..5 in .env"
        )

    last_error = None

    for key in keys:
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",  # Use a recent stable model
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )

            # The response object may have .text or
            # .candidates[0].content.parts[0].text
            if hasattr(response, "text"):
                return response.text
            elif hasattr(response, "candidates") and response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                raise ValueError("Unexpected response format")

        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(
        f"All Gemini API keys failed. Last error: {last_error}"
    )


def parse_ai_response(text: str) -> Dict[str, Any]:
    """Extract structured info from the AI response (optional)."""

    # For now, just return the whole text
    return {
        "explanation": text,
        "suggestions": [],
        "concepts": []
    }


def analyze_circuit(
    ast: CircuitAST,
    statevector: Optional[Any] = None,
    user_query: str = ""
) -> Dict[str, Any]:
    """Combine error checking and AI analysis."""
    from .checker import get_circuit_errors

    errors = get_circuit_errors(ast, statevector)
    circuit_data = serialize_circuit(ast)
    prompt = build_prompt(circuit_data, errors, user_query)

    try:
        ai_text = get_ai_response(prompt)
        parsed = parse_ai_response(ai_text)
    except Exception as e:
        parsed = {
            "explanation": f"AI analysis failed: {e}",
            "suggestions": [],
            "concepts": []
        }

    return {
        "errors": errors,
        "explanations": parsed,
        "circuit_summary": circuit_data
    }
