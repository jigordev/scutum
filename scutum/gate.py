from typing import Union, List, Dict, Any, Optional
from scutum.types import Rule
from scutum.scope import Scope
from scutum.policy import Policy
from scutum.response import Response
from scutum.exceptions import AuthorizationException

class Gate:
    def __init__(
            self,
            rules: Optional[Dict[str, Rule]] = None,
            policies: Optional[Dict[str, Policy]] = None
        ):
        self._scope = Scope("default")
        
        if rules:
            for rule, func in rules.items():
                self._register_rule(rule, func)

        if policies:
            for name, policy in policies.items():
                self._register_policy(name, policy)

    def has_rule(self, name: str):
        return self._scope.has_rule(name)

    def has_scope(self, name: str):
        return self._scope.has_scope(name)
    
    def clear(self):
        self._scope = Scope("default")
    
    def rules(self):
        return self._scope._rules
    
    def scopes(self):
        return self._scope._childrens
    
    def _register_rule(self, name: str, rule: Rule):
        if not callable(rule):
            raise TypeError("Rule must be a callable")
        self._scope.add_rule(name, rule)
            
    def _register_policy(self, name: str, policy: Policy):
        if not isinstance(policy, type) or not issubclass(policy, Policy):
            raise TypeError("policy must be a Policy class (not an instance)")

        if self._scope.has_scope(name):
            raise KeyError(f"a scope named {name} alredy exists")

        rules = policy._to_rules()
        for rule, func in rules.items():
            self._register_rule(f"{name}:{rule}", func)
        
    def add_scope(self, name: str, scope: Scope):
        if self._scope.has_scope(name):
            raise KeyError(f"A scope named {name} alredy exists")
        self._scope.add_scope(name, scope)

    def _call_rule(self, name: str, *args, **kwargs):
        return self._scope.call(name, *args, **kwargs)

    def rule(self, name: str):
        def decorator(rule: Rule):
            self._register_rule(name, rule)
            return rule
        return decorator
    
    def add_rule(self, name: str, rule: Rule):
        if self._scope.has_rule(name):
            raise KeyError(f"A rule named {name} alredy exists")
        self._register_rule(name, rule)
    
    def policy(self, name):
        def decorator(policy: Policy):
            self._register_policy(name, policy)
            return policy
        return decorator
    
    def add_policy(self, name, policy):
        self._register_policy(name, policy)
    
    def remove_rule(self, name: str):
        self._scope.remove_rule(name)

    def remove_scope(self, name: str):
        self._scope.remove_scope(name)

    def check(self, rule: str, user: Any, *args, **kwargs) -> Union[Response, bool]:
        result = self._call_rule(rule, user, *args, **kwargs)
        if isinstance(result, Response):
            return result
        return bool(result)

    def allowed(self, rule: str, user: Any, *args, **kwargs) -> bool:
        response = self.check(rule, user, *args, **kwargs)
        if isinstance(response, Response):
            return response.allowed
        return response

    def denied(self, rule: str, user: Any, *args, **kwargs) -> bool:
        response = self.check(rule, user, *args, **kwargs)
        if isinstance(response, Response):
            return not response.allowed
        return not response
    
    def authorize(self, rule: str, user: Any, *args, **kwargs) -> None:
        response = self.check(rule, user, *args, **kwargs)
        if isinstance(response, Response):
            response.authorize()

        if isinstance(response, bool) and not response:
            raise AuthorizationException()
    
    def any(self, rules: List[str], user: Any, *args, **kwargs):
        return any([self.allowed(rule, user, *args, **kwargs) for rule in rules])

    def none(self, rules: List[str], user: Any, *args, **kwargs):
        return not self.any(rules, user, *args, **kwargs)
