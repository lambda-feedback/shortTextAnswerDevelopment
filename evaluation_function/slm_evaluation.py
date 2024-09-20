from gpt4all import GPT4All
import time
from typing import Any, TypedDict
try:
    # from .evaluation_response_utilities import EvaluationResponse
    from .evaluation_response import Result as EvaluationResponse              # NOTE: instead of importing from lf_toolkit.evaluation as more attributes are added to the class
    from .slm_instructions import build_instruction
    from .nlp_evaluation import evaluation_function as nlp_evaluation_function
except ImportError:
    # from evaluation_response_utilities import EvaluationResponse
    from evaluation_response import Result as EvaluationResponse
    from slm_instructions import build_instruction
    from nlp_evaluation import evaluation_function as nlp_evaluation_function


class Params(TypedDict):
    pass

model = GPT4All(model_name="Phi-3.5-mini-instruct-Q6_K.gguf",model_path="evaluation_function/models/", allow_download=False) # downloads / loads the model
# instruction = "Compare the following two sections: Response='{response}' & Answer='{answer}'. Write 'True' if the response perfectly matches the answer, 'False' otherwise. Do not provide any explanation."

def evaluation_function(response: Any, answer: Any, params: Any) -> EvaluationResponse:
    """
    Function used to evaluate a student response.
    ---
    The handler function passes three arguments to evaluation_function():

    - `response` which are the answers provided by the student.
    - `answer` which are the correct answers to compare against.
    - `params` which are any extra parameters that may be useful,
        e.g., error tolerances.

    The output of this function is what is returned as the API response
    and therefore must be JSON-encodable. It must also conform to the
    response schema.

    Any standard python library may be used, as well as any package
    available on pip (provided it is added to requirements.txt).

    The way you wish to structure you code (all in this function, or
    split into many) is entirely up to you. All that matters are the
    return types and that evaluation_function() is the main function used
    to output the evaluation response.
    """
    start_time = time.process_time()

    eval_response = EvaluationResponse() 
    eval_response.is_correct = False
    eval_response.add_evaluation_type("slm")
    evaluation_instruction = ""
    
    """
    (Reverted) Cases for exact_match or inclusion of a given word to distinguish between instruction prompts for the model
        -> such checks are done by the NLP algorithm and not by the model
        -> model only checks for context similarity between the response and the answer

        Should still use the keystrings and check if the response contains something similar to them.
            -> exact_match looks if that keystring appears in the response (done by NLP)
            -> otherwise check if similar words are present in the response (done by SLM)

    TODO: Could the eval function receive the question for context checking? 
    """

    # STEP 1: check if the keystrings are present in the response (contextually)
    problematic_keystrings = []
    if params is not None and "keystrings" in params:
        keystrings = params["keystrings"]
        for keystring_object in keystrings:
            keystring = keystring_object['string']      # string that evaluation and feedback will be focused on
            
            # check if the keystring is found in the response or if something similar is contained in the response
            keystring_instruction = build_instruction(response, answer, "include_word", keystring)
            keystring_llm_response = model.generate(keystring_instruction, max_tokens=10)
            if not process_response_corectness(keystring_llm_response):
                # if the keystring is not found in the response, add it to the list of problematic keystrings
                problematic_keystrings.append(keystring)
                # print(keystring_instruction)
                # print("Keystring not found in response: ", keystring)

    # STEP 2: default to similarity case if no parameters are provided
    evaluation_instruction = build_instruction(response, answer, "similarity")

    with model.chat_session():
        llm_response = model.generate(evaluation_instruction, max_tokens=10)
        end_time = time.process_time()

        eval_response.add_processing_time(end_time - start_time)
        eval_response.add_metadata("response", response)
        is_correct = process_response_corectness(llm_response)
        feedback = ""
        if is_correct is not None:
            eval_response.is_correct = is_correct
            if problematic_keystrings.__len__() > 0:
                if is_correct:
                    feedback = "The response is ALMOST correct. However, the response should also focus on ideas regarding: " + ", ".join(problematic_keystrings)
                else:
                    feedback = "The response is incorrect. The response should focus on ideas regarding: " + ", ".join(problematic_keystrings)
                # even if the similarity decided that the response is correct, the problematic keystrings override this decision
                eval_response.is_correct = False
            else:
                feedback = "The response is contextually {}.".format("correct" if is_correct else "incorrect")
            # eval_response.add_feedback(("feedback", feedback))
            eval_response.add_feedback("feedback", feedback) # NOTE: lf_toolkit Result in evaluation_response.py
        else:
            eval_response.is_correct = False
            feedback = "<LLM RESPONSE ERROR> The response could not be evaluated."
            # eval_response.add_feedback(("feedback", feedback))
            eval_response.add_feedback("feedback", feedback) # NOTE: lf_toolkit Result in evaluation_response.py

        # print("~~~~~~~~~~~~~~~~")
        # print("Instruction: ", evaluation_instruction)
        # print("Feedback:", llm_response)
        # for feedback_index in eval_response.get_feedback("feedback"):
        #     print(eval_response._feedback[feedback_index])
        # print("-- Time taken to generate response: ", end_time - start_time, " seconds --")

    return eval_response

def process_response_corectness(result: Any) -> bool:
    result = result.lower()
    if "true" in result:
        return True
    elif "false" in result:
        return False
    else:
        return None