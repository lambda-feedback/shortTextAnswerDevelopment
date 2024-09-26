class EvaluationResponse:
    def __init__(self):
        self.is_correct = False
        self.latex = None
        self._feedback = []  # A list that will hold all feedback items
        self._feedback_tags = {}  # A dictionary that holds a list with indices to all feedback items with the same tag
        self._metadata = {}
        self._processing_time = 0
        self._evaluation_type = None

    def get_feedback(self, tag):
        return self._feedback_tags.get(tag, None)

    def get_tags(self):
        return list(self._feedback_tags.keys())
    
    def get_processing_time(self):
        return self._processing_time
    
    def get_is_correct(self):
        return self.is_correct
    
    def get_evaluation_type(self):
        return self._evaluation_type

    def add_feedback(self, feedback_item):
        # Adds a feedback item to the feedback list and tags it.
        # Expects feedback_item to be a tuple (tag, feedback).
        if isinstance(feedback_item, tuple):
            self._feedback.append(feedback_item[1])
            if feedback_item[0] not in self._feedback_tags.keys():
                self._feedback_tags.update({feedback_item[0]: [len(self._feedback)-1]})
            else:
                self._feedback_tags[feedback_item[0]].append(len(self._feedback)-1)
        else:
            raise TypeError("Feedback must be on the form (tag, feedback).")

    def add_metadata(self, name, data):
        self._metadata.update({name: data})
    
    def add_processing_time(self, time):
        self._processing_time = time

    def add_evaluation_type(self, evaluation_type):
        self._evaluation_type = evaluation_type

    def _serialise_feedback(self) -> str:
        feedback = []
        for x in self._feedback:
            if (isinstance(x, tuple) and len(x[1].strip())) > 0:
                feedback.append(x[1].strip())
            elif len(x.strip()) > 0:
                feedback.append(x.strip())
        return "<br>".join(feedback)

    def serialise(self, include_test_data=False) -> dict:
        out = dict(is_correct=self.is_correct, feedback=self._serialise_feedback())
        if include_test_data:
            # if include_test_data is true, then add the other metadata, if false (as aws is by default setting it to false)
            out.update(dict(tags=list(self._feedback_tags.keys())))
            if len(self._metadata) > 0:
                out.update(dict(metadata=self._metadata))
            if self._processing_time >= 0:
                out.update(dict(processing_time=self._processing_time))
            if self._evaluation_type is not None:
                out.update(dict(evaluation_type=self._evaluation_type))
        return out

    def __getitem__(self, key):
        return self.serialise(include_test_data=True)[key]