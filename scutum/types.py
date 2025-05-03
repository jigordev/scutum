from typing import Callable, Union
from scutum.response import Response

Rule = Callable[..., Union[Response, bool]]