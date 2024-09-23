def build_instruction(response, answer, case, keystring=""):
    """
    Build instruction for the SLM task
    """

    if case == 'include_word':
        # CASE for keystring check
        case = include_word.format(keystring=keystring)
        instruction = example_scenario_keystring + base_instruction_keystring.format(keystring=keystring, answer=answer, case=case)
    elif case == 'exclude_word':
        # NOTE: (should_countain == false) this is done by NLP function
        case = exclude_word.format(keystring=keystring)
    elif case == 'similarity':
        # DEFAULT CASE for whole sentence check
        case = similarity + " or if " + include
        instruction = example_scenario + base_instruction.format(response=response, answer=answer, case=case)
    elif case == 'TEST':
        # TEST CASE
        instruction = base_prompt.format(response=response, answer=answer)
    elif case == 'rephrase':
        # CASE for rephrasing
        instruction = feedback_rephrasing_prompt.format(correct_answer=answer, student_response=response, student_info=keystring)
    elif case == 'rephrase_custom':
        # CASE for rephrasing custom feedback
        instruction = custom_feedback_rephrasing_prompt.format(custom_feedback=keystring)
    else:
        raise ValueError("Invalid case. Please provide a valid case: 'include', 'exclude_word' or 'similarity'")


    return instruction

example_scenario = """Example Response='A cat is in the house' & Example Answer='A dog is in the house' -> False; 
Example Response='John's cat is in the house' & Example Answer='An animal in the building' -> True; \n"""
base_instruction = "Write 'True' if {case}; 'False' otherwise. Do not provide any explanation. \nResponse='{response}' & Answer='{answer}' ->"

example_scenario_keystring = """Example Keystrings='generate fake data' & Example Answer='The algorithm generates false data.' -> True;
Example Keystrings='generate fake data' & Example Answer='The algorithm receives data of fake people.' -> False; \n"""
base_instruction_keystring = "Write 'True' if {case}; 'False' otherwise. Do not provide any explanation. \nKeystrings='{keystring}' & Answer='{answer}' ->"

# CASES for evaluation
# Include, Exclude of words are done by an algorithm and not by the model
perfect_match = "the Response perfectly matches the Answer"
include_word = "the Response contains mentions the '{keystring}' or describes something similar"
exclude_word = "the Response does not contain '{keystring}'"
similarity = "the Response is similar to or describes the Answer"
include = "the Response is a subset of the Answer"          # descriptive version

base_prompt = """You are an expert educator tasked with rigorously comparing student responses to correct answers. Carefully evaluate each response, looking for errors, misunderstandings, or deviations in meaning, including issues of precision, negation, missing details, or conceptual differences. If the student demonstrates partial understanding, identify exactly where they made a mistake and what they got right.

Provide a score from 0 to 1, where:
- 1 means the responses are identical in meaning,
- 0 means they are completely unrelated or opposite,
- Intermediate values (e.g., 0.5) represent partial understanding.

Correct answer: "{answer}"
Student response: "{response}"

Score: [Insert score]
Comment: [Insert explanation about the discrepancies found.]

"""

feedback_rephrasing_prompt = """You are an expert educator tasked with providing helpful feedback using the below information on the student's response on a question:
Correct answer: '{correct_answer}'
Student response: '{student_response}'
Feedback information: '{student_info}'
Be sure to provide constructive feedback that helps the student understand their mistakes and improve their understanding of the topic. 
Be clear and concise in your feedback, and provide examples where necessary.
The feedback must be maximally 100 words.

A:
"""
# NOTE: it was noticed that Phi-3 starts its response with 'A:' 

custom_feedback_rephrasing_prompt = """You are an expert educator tasked with rephrasing the below feedback:
Feedback information: '{custom_feedback}'

A:"""