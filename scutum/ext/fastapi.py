from typing import Callable, Any
from scutum import Gate
from fastapi import Depends, HTTPException

class AuthConfig:
    def __init__(self, get_current_user: Callable = None):
        self.get_current_user = get_current_user

auth_config = AuthConfig()

def check_permission(action: str, gate: Gate, status=403, message="Unauthorized"):
    def checker(
        user: Any = Depends(lambda: auth_config.get_current_user()),
        *args,
        **kwargs
    ):
        if gate.denied(action, user, *args, **kwargs):
            raise HTTPException(status_code=status, detail=message)
        
        return True
    return checker
