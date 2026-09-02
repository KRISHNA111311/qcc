import json
import logging
from typing import Dict, Any, Optional
from google import genai

from ..config import get_settings
from ..core.models import CircuitAST

logger = logging.getLogger(__name__)

def analyze_circuit(ast: CircuitAST, statevector: Optional[Any] = None, user_query: str = "") -> Dict[str, Any]:
    from .checker import get_circuit_errors

    errors = get_circuit_errors(ast, statevector)

    # Build a prompt that asks for a short answer
    gates_str = ", ".join([f"{g.type.value}({','.join(map(str, g.qubits))})" for g in ast.operations])
    prompt = (
        f"Circuit with {ast.num_qubits} qubits: {gates_str}. "
        f"Question: {user_query if user_query else 'Explain what this circuit does in 2-3 sentences.'}"
    )
    logger.info(f"Prompt: {prompt}")

    ai_result = {"explanation": "", "suggestions": [], "concepts": []}

    settings = get_settings()
    keys = settings.GEMINI_API_KEYS
    if not keys:
        ai_result["explanation"] = "No Gemini API keys configured."
        return {"errors": errors, "explanations": ai_result, "circuit_summary": {"num_qubits": ast.num_qubits, "operations": len(ast.operations)}}

    # Use ONLY the first key
    key = keys[0]
    client = genai.Client(api_key=key, http_options={"timeout": 120})

    try:
        interaction = client.interactions.create(
            model="gemini-3.6-flash",  # your working model
            input=prompt,
            timeout=120
        )
        if hasattr(interaction, 'output_text'):
            ai_result["explanation"] = interaction.output_text
            logger.info("AI response received.")
        else:
            ai_result["explanation"] = "Response missing output_text"
    except Exception as e:
        error_msg = f"AI failed: {str(e)}"
        logger.error(error_msg)
        ai_result["explanation"] = error_msg

    return {
        "errors": errors,
        "explanations": ai_result,
        "circuit_summary": {"num_qubits": ast.num_qubits, "operations": len(ast.operations)}
    }
