# ShortTextAnswer
This function evaluates the similarity value between two short texts, as well as identifying certain key strings in a student's answer.

## Inputs
`keystrings` - Optional parameter. Represents a list of keystring objects which the function will search for in the answer.

### `keystring` object
The `keystring` object contains several fields which affect how it will be interpreted:

* `string` - Required. The actual keystring being searched for.
* `exact_match` - Optional. A boolean value indicating whether to search for the exact string or for a semantically similar one. Defaults to `false`
* `should_contain` - Optional. A boolean value indicating whether it is expected for the keystring to be found in the answer or not. Defaults to `true`. Setting this flag to false indicates that a correct response will not contain the specified keystring.
* `custom_feedback` - Optional. A feedback string to be returned if the `string` was not found (or if it was, in case `should_contain` was set to `false`). Defaults to `None`, in which case a generic response will be generated containing the string searched for.

## Outputs
The function will return an object with 3 fields of interest. the `is_correct` and `feedback` fields are required by LambdaFeedback to present feedback to the user. The `result` field is only used for development.
```python
{
    "is_correct": "<bool>",
    "result": {
        "response": "<string>",
        "processing_time": "<double>",
    },
    "feedback": "string"
}
```

* `response` - The student answer. USed for debugging purposes.
* `processing_time` - The time it took for the function to evaluate

If the function identified a problematic keystring, the result object will have an additional field:
* `keystring-scores` - list(string, double). List of the provided keystrings and their best similarity scores that were found in the answer.

Otherwise, it will have the additional fields:
* `method` - string. Either "w2v" or "BOW vector similarity".
* `similarity_value` - double. The similarity value between the response and the answer.

If the method is w2v, it means the two texts were found to be similar. Otherwise, a BOW vector similarity check is performed in order to identify the most likely word that caused the texts to be found dissimilar.

## Initial SetUp
Follow Docker Image instructions and run 
`docker build -t <image_name> .` in app/

Otherwise if setup locally:
1. create a venv
2. in the venv `pip install -r app/requirements.txt`
3. if errors encountered with nltk packages, follow `testing_nltk.py` instructions

## Examples
*List of example inputs and outputs for this function, each under a different sub-heading*

### Example simple input, no keystring

Input
```python
{
    "response": "Density, velocity, viscosity, length",
    "answer": "Density, speed, Viscosity, Length",
}
```

Output
```python
{
    'is_correct': True, 
    'result': {
        'response': 'Density, speed, Viscosity, Length',
        'processing_time': 0.022912219000000178, 
        'method': 'w2v', 
        'similarity_value': 0.9326027035713196}, 
    'feedback': 'Confidence: 0.933%'
}
```

### Example keystring input

Input
```python
{
    "response": "Molecules are made out of atoms",
    "answer": "Many atoms form a molecule",
    'keystrings': [
        {'string': 'molecule'}, 
        {'string': 'proton', 'exact_match': True}
    ]
}
```

Output
```python
{
    'is_correct': False, 
    'result': {
        'response': 'Molecules are made out of atoms', 
        'processing_time': 0.30640586500000033, 
        'keystring-scores': [
            ('molecule', 0.990715997949492), 
            ('proton', 0.9186190596675989) # Searched for with exact match, therefore not a match.
        ]
    }, 
    'feedback': "Cannot determine if the answer is correct. Please provide more information about 'proton'"}
```