from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union


FeedbackItem = Tuple[str, str]


def update_feedback(
    feedback: Dict[str, List[str]], feedback_items: List[FeedbackItem]
) -> Dict[str, List[str]]:
    for item in feedback_items:
        if (isinstance(item, tuple) or isinstance(item, list)) and len(item) == 2:
            feedback.setdefault(item[0], []).append(item[1])
        else:
            raise TypeError("Feedback item must be a tuple of (tag, feedback).")

    return feedback


class Result:
    __slots__ = ("is_correct", "response_latex", "response_simplified", "_feedback",
                 "_metadata", "_processing_time", "_evaluation_type")
    __fields__ = (
        "is_correct",
        "response_latex",
        "response_simplified",
        "feedback",
        "tags",
        "metadata",
        "processing_time",
        "evaluation_type"
    )

    is_correct: bool
    response_latex: str
    response_simplified: str

    _feedback: Dict[str, List[str]]

    _metadata: Dict[str, Any]
    _processing_time: float
    _evaluation_type: str

    def __init__(
        self,
        is_correct: bool = False,
        latex: str = "",
        simplified: str = "",
        feedback_items: List[FeedbackItem] = [],
        metadata: Dict[str, Any] = {},
        processing_time: float = 0,
        evaluation_type: str = None,
    ):
        self.is_correct = is_correct
        self.response_latex = latex
        self.response_simplified = simplified
        self._feedback = update_feedback({}, feedback_items)
        self._metadata = metadata
        self._processing_time = processing_time
        self._evaluation_type = evaluation_type

    @property
    def feedback(self) -> str:
        return "<br>".join(
            [
                feedback_str
                for lists in self._feedback.values()
                for feedback_str in lists
            ]
        )

    @property
    def tags(self) -> Union[List[str], None]:
        return list(self._feedback.keys())
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata


    def get_feedback(self, tag: str) -> List[str]:
        return self._feedback.get(tag, [])
    
    def get_is_correct(self) -> bool:
        return self.is_correct
    
    def get_processing_time(self) -> float:
        return self._processing_time
    
    def get_evaluation_type(self) -> str:
        return self._evaluation_type

    def add_feedback(self, tag: str, feedback: str) -> None:
        self._feedback.setdefault(tag, []).append(feedback)

    def add_metadata(self, name: str, data: Any) -> None:
        self._metadata[name] = data

    def add_processing_time(self, time: float) -> None:
        self._processing_time = time

    def add_evaluation_type(self, evaluation_type: str) -> None:
        self._evaluation_type = evaluation_type

    def to_dict(self, include_test_data: bool = False) -> Dict[str, Any]:
        res = {
            "is_correct": self.is_correct,
            "feedback": self.feedback,
        }

        if self.response_simplified:
            res["response_simplified"] = self.response_simplified
        if self.response_latex:
            res["response_latex"] = self.response_latex
        if include_test_data:
            res["tags"] = self.tags
            if len(self._metadata) > 0:
                res["metadata"] = self._metadata
            if self._processing_time >= 0:
                res["processing_time"] = self._processing_time
            if self._evaluation_type:
                res["evaluation_type"] = self._evaluation_type

        return res

    def __repr__(self):
        members = ", ".join(f"{k}={repr(getattr(self, k))}" for k in self.__fields__)
        return f"Result({members})"

    def __eq__(self, other):
        if type(self) is not type(other):
            return False

        for k in self.__slots__:
            if getattr(self, k) != getattr(other, k):
                return False

        return True