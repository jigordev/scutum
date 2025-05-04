from typing import Protocol, Union
from scutum.response import Response

class Rule(Protocol):
    def __call__(self, *args, **kwargs) -> Union[Response, bool]:
        ...