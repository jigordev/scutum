from typing import Protocol, Union, Awaitable
from scutum.response import Response

ReturnType = Union[Response, bool]

class Rule(Protocol):
    def __call__(self, *args, **kwargs) -> Union[ReturnType, Awaitable[ReturnType]]:
        ...