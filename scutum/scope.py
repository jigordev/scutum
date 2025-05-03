from typing import List, Dict, Optional, Tuple
from scutum.types import Rule
from scutum.exceptions import RuleNotFoundException, ScopeNotFoundException

class Scope:
    def __init__(
        self,
        name: str,
        parent: Optional["Scope"] = None,
        childrens: Optional[List["Scope"]] = None
    ):
        self.name = name
        self._rules: Dict[str, Rule] = {}
        self._childrens: Dict[str, Scope] = {}
        self._parent: Optional["Scope"] = parent

        if parent is not None:
            parent.add_scope(name, self)

        if childrens:
            for child in childrens:
                self.add_scope(child.name, child)

    def has_rule(self, name: str) -> bool:
        try:
            self._resolve_rule(name)
            return True
        except RuleNotFoundException:
            return False
    
    def get_rule(self, name: str) -> Rule:
        return self._resolve_rule(name)

    def add_rule(self, name: str, rule: Rule):
        scope, rule_name = self._resolve_path(name)
        scope._rules[rule_name] = rule

    def remove_rule(self, name: str):
        scope, rule_name = self._resolve_path(name)
        if rule_name not in scope._rules:
            raise RuleNotFoundException(f"Rule '{rule_name}' not found")
        del scope._rules[rule_name]

    def has_scope(self, name: str) -> bool:
        try:
            self._resolve_scope(name)
            return True
        except ScopeNotFoundException:
            return False

    def get_scope(self, name: str) -> "Scope":
        return self._resolve_scope(name)

    def add_scope(self, name: str, scope: "Scope"):
        parent_scope, child_name = self._resolve_path(name)
        parent_scope._childrens[child_name] = scope
        scope._parent = parent_scope

    def remove_scope(self, name: str):
        parent_scope, child_name = self._resolve_path(name)
        if child_name not in parent_scope._childrens:
            raise ScopeNotFoundException(f"Scope '{child_name}' not found")
        del parent_scope._childrens[child_name]

    def call(self, name: str, *args, **kwargs):
        rule = self.get_rule(name)
        return rule(*args, **kwargs)

    def _resolve_scope(self, path: str) -> "Scope":
        scopes = path.split(":")
        current = self
        for name in scopes:
            if name not in current._childrens:
                raise ScopeNotFoundException(f"Scope '{name}' not found")
            current = current._childrens[name]
        return current

    def _resolve_rule(self, path: str) -> Rule:
        scope, rule_name = self._resolve_path(path)
        if rule_name not in scope._rules:
            raise RuleNotFoundException(f"Rule '{rule_name}' not found")
        return scope._rules[rule_name]

    def _resolve_path(self, path: str) -> Tuple["Scope", str]:
        parts = path.split(":")
        if len(parts) == 1:
            return self, parts[0]
        scope_path = ":".join(parts[:-1])
        return self._resolve_scope(scope_path), parts[-1]

    def debug(self, indent: int = 0):
        prefix = "  " * indent
        print(f"{prefix}Scope: {self.name}")
        for rule_name in self._rules:
            print(f"{prefix}  Rule: {rule_name}")
        for child in self._childrens.values():
            child.debug(indent + 1)
