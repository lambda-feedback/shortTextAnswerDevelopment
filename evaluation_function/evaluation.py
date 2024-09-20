from typing import Any
# from lf_toolkit.evaluation import Result, Params

try:
    from .nlp_evaluation import evaluation_function as nlp_evaluation_function
except ImportError:
    from nlp_evaluation import evaluation_function as nlp_evaluation_function

try:
    from .slm_evaluation import evaluation_function as slm_evaluation_function
except ImportError:
    from slm_evaluation import evaluation_function as slm_evaluation_function

try:
    from .evaluation_response_utilities import EvaluationResponse
except ImportError:
    from evaluation_response_utilities import EvaluationResponse

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

    eval_response = EvaluationResponse()
    eval_response.is_correct = False
    include_test_data = False

    if "include_test_data" in params:
        include_test_data = params["include_test_data"]

    # NOTE: Layer responses are classes and are not serialised
    eval_response_nlp = nlp_evaluation_function(response, answer, params)
    eval_response_slm = slm_evaluation_function(response, answer, params)

    """
    Looking for different mistake scenarios
    """
    # print(eval_response_nlp.serialise(include_test_data=include_test_data), eval_response_slm.serialise(include_test_data=include_test_data))
    if eval_response_nlp.is_correct and eval_response_slm.is_correct:
        eval_response.is_correct = True
        eval_response.add_feedback(("feedback", "The response is correct (matched key points and follows the right context)."))
    elif eval_response_slm.is_correct and eval_response_nlp["metadata"]["similarity_value"] > 0.75: # set threshold in nlp_evaluation
        eval_response.is_correct = False
        eval_response.add_feedback(("feedback", "The response is ALMOST correct. But the student missed some key points. " + eval_response_nlp["feedback"] + " " + eval_response_slm["feedback"]))
    elif eval_response_slm.is_correct and eval_response_nlp["metadata"]["similarity_value"] <= 0.75:
        eval_response.is_correct = False
        eval_response.add_feedback(("feedback", "The response is incorrect as the student missed some key points. " + eval_response_nlp["feedback"] + " " + eval_response_slm["feedback"]))
    elif eval_response_nlp.is_correct:
        eval_response.is_correct = False
        eval_response.add_feedback(("feedback", "The response has pointed out all the key ideas, but its context is wrong. " + eval_response_nlp["feedback"] + " " + eval_response_slm["feedback"]))
    else:
        eval_response.is_correct = False
        eval_response.add_feedback(("feedback", "The response is incorrect as its context is wrong. " + eval_response_nlp["feedback"] + " " + eval_response_slm["feedback"]))

    return eval_response.serialise(include_test_data=include_test_data)