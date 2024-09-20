from gpt4all import GPT4All
import time
from typing import Any, TypedDict

try:
    from .slm_instructions import build_instruction
    from .slm_evaluation import model
except ImportError:
    from slm_instructions import build_instruction
    from slm_evaluation import model

def rephrase_feedback(response: Any, answer: Any, info: Any) -> Any:
    instruction = build_instruction(response, answer, 'rephrase', info)
    # print(instruction)
    response = model.generate(instruction, max_tokens=150)

    processed_response = process_llm_response(response)
    # print(processed_response)
    return processed_response

def process_llm_response(response: Any) -> Any:
    """
    Process the LLM response have first paragraph only
    """
    if '\n' in response:
        return response.split("\n")[0]
    return response
