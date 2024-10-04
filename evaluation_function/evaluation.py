from typing import Any
import time
# from lf_toolkit.evaluation import Result, Params

try:
    from .nlp_evaluation import evaluation_function as nlp_evaluation_function
    from .slm_evaluation import evaluation_function as slm_evaluation_function
    # from .evaluation_response_utilities import EvaluationResponse as EvaluationResponse_old
    from .evaluation_response import Result as EvaluationResponse              # NOTE: instead of importing from lf_toolkit.evaluation as more attributes are added to the class
    from .slm_rephraser import rephrase_feedback
except ImportError:
    from nlp_evaluation import evaluation_function as nlp_evaluation_function
    from slm_evaluation import evaluation_function as slm_evaluation_function
    # from evaluation_response_utilities import EvaluationResponse as EvaluationResponse_old
    from evaluation_response import Result as EvaluationResponse
    from slm_rephraser import rephrase_feedback


def evaluation_function(
    response: Any,
    answer: Any,
    params: Any,
) -> EvaluationResponse:
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


    Function that combines the NLP and SLM evaluation functions to provide a final evaluation overseeing the:
    - correctness of the response from the perspective of the key points
    - correctness of the context of the response

    Params:
    - include_test_data: A boolean that determines whether to include other data in the EvaluationResponse output

    Output:
    - EvaluationResponse: A class that contains the evaluation results with feedback
    """
    start_time = time.process_time()

    eval_response = EvaluationResponse()
    eval_response.is_correct = False
    include_test_data = False

    if "include_test_data" in params:
        include_test_data = params["include_test_data"]

    # NOTE: Layer responses are classes and are not serialised
    eval_response_nlp = nlp_evaluation_function(response, answer, params)
    eval_response_slm = slm_evaluation_function(response, answer, params)
    eval_response.add_metadata("nlp_similarity_value", eval_response_nlp.metadata["similarity_value"])
    eval_response.add_metadata("nlp_processing_time", eval_response_nlp.get_processing_time())
    eval_response.add_metadata("slm_processing_time", eval_response_slm.get_processing_time())

    """
    Looking for different mistake scenarios
    """
    # print(eval_response_nlp.serialise(include_test_data=include_test_data), eval_response_slm.serialise(include_test_data=include_test_data))
    feedback_layers, tag, is_correct = response_handler(eval_response_nlp, eval_response_slm)

    # STEP A: check for custom feedback tag in the feedback
    custom_feedback, custom_feedback_layers = check_custom_feedback(eval_response_nlp.feedback)
    if custom_feedback:
        tag = "CUSTOM_FEEDBACK"
        feedback_layers = custom_feedback_layers

    # STEP B: Use the SLM to rephrase the feedback
    rephrased_feedback = rephrase_feedback(response, answer, feedback_layers, custom_feedback)

    # eval_response.add_feedback(("feedback", rephrased_feedback))
    eval_response.add_feedback("feedback", rephrased_feedback) # NOTE: lf_toolkit Result in evaluation_response.py
    eval_response.is_correct = is_correct
    eval_response.add_metadata("tag", tag)

    end_time = time.process_time()
    eval_response.add_processing_time(end_time - start_time)

    # NOTE: expected serialised output for the server handler called by main.py
    return eval_response.to_dict(include_test_data=include_test_data)

def response_handler(eval_response_nlp, eval_response_slm) -> Any:
    tag = ""
    feedback_layers = ""
    is_correct = False

    if eval_response_nlp.is_correct and eval_response_slm.is_correct:
        is_correct = True
        feedback_layers = "The response is correct (matched key points and follows the right context)."
        tag = "FEEDBACK_SLM_PASS_NLP_PASS"
    elif eval_response_slm.is_correct and eval_response_nlp.metadata["similarity_value"] > 0.75: # set threshold in nlp_evaluation
        is_correct = False
        feedback_layers = "The response is ALMOST correct. But the student missed some key points. " + eval_response_nlp.feedback + " " + eval_response_slm.feedback
        tag = "FEEDBACK_SLM_PASS_NLP_ALMOST_FAIL"
    elif eval_response_slm.is_correct and eval_response_nlp.metadata["similarity_value"] <= 0.75:
        is_correct = False
        feedback_layers = "The response is incorrect as the student missed some key points. " + eval_response_nlp.feedback + " " + eval_response_slm.feedback
        tag = "FEEDBACK_SLM_PASS_NLP_FAIL"
    elif eval_response_nlp.is_correct:
        is_correct = False
        feedback_layers = "The response has pointed out all the key ideas, but its context is wrong." + eval_response_nlp.feedback + " " + eval_response_slm.feedback
        tag = "FEEDBACK_SLM_FAIL_NLP_PASS"
    else:
        is_correct = False
        feedback_layers = "The response is incorrect as its context is wrong. " + eval_response_nlp.feedback + " " + eval_response_slm.feedback
        tag = "FEEDBACK_SLM_FAIL_NLP_FAIL"

    return feedback_layers, tag, is_correct

def check_custom_feedback(feedback):
    if "CUSTOM_FEEDBACK" in feedback:
        # cut out the CUSTOM_FEEDBACK tag from the feedback and return the feedback
        return True, feedback.replace("CUSTOM_FEEDBACK", "")
    return False, feedback

# if __name__ == "__main__":
#     responses = [
#         "A GAN is a type of algorithm used to detect fake data on the internet.",
#         "A GAN is a network that generates data based on fake examples."
#     ]
#     answer = "A Generative Adversarial Network (GAN) is a type of machine learning model composed of two neural networks: a generator and a discriminator. The generator creates fake data, while the discriminator tries to distinguish between real and fake data. Through this adversarial process, both networks improve over time, and the generator eventually becomes capable of producing data that closely resembles the real data."
    
#     for response in responses:
#         llm_response = evaluation_function(response, answer, {"include_test_data": True})
#         print("--------------------")
