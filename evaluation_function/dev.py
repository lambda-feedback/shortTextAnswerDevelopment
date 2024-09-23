import sys
import json

# from lf_toolkit.shared.params import Params

from .evaluation import evaluation_function

def dev():
    """Run the evaluation function from the command line for development purposes.

    Usage: python -m evaluation_function.dev <answer> <response>
    """
    if len(sys.argv) < 3:
        print("Usage: python -m evaluation_function.dev <answer> <response>")
        return
    
    answer = sys.argv[1]
    response = sys.argv[2]
    params = sys.argv[3] if len(sys.argv[3]) > 0 else dict()
    # parse params into a dict
    try:
        params = json.loads(params)
    except json.JSONDecodeError:
        print("Invalid JSON string for params")
        return
    
    if 'include_test_data' not in params:
        params['include_test_data'] = False

    print(f"Answer: {answer}")
    print(f"Response: {response}")
    print(f"Params: {params}")

    result = evaluation_function(answer, response, params)

    print(result.to_dict())

if __name__ == "__main__":
    dev()