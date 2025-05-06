import inspect
from asyncio import Lock
from threading import RLock
from abc import ABC, abstractmethod
from typing import Dict, Optional
from scutum.types import Rule
from scutum.exceptions import RuleNotFoundException, ScopeNotFoundException

class BaseScope(ABC):
    def __init__(self, name: str):
        self.name = name
        self._rules: Dict[str, Rule] = {}
        self._children: Dict[str, "BaseScope"] = {}
        self._parent: Optional["BaseScope"] = None

    @abstractmethod
    def debug(self, indent: int = 0):
        ...

class ScopeResolverMixin:
    def _resolve_scope(self, path: str):
        scopes = path.split(":")
        current = self
        for name in scopes:
            if name not in current._children:
                raise ScopeNotFoundException(f"Scope '{name}' not found")
            current = current._children[name]
        return current

    def _resolve_rule(self, path: str) -> Rule:
        scope, rule_name = self._resolve_path(path)
        if rule_name not in scope._rules:
            raise RuleNotFoundException(f"Rule '{rule_name}' not found")
        return scope._rules[rule_name]

    def _resolve_path(self, path: str):
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
        for child in self._children.values():
            child.debug(indent + 1)

class Scope(BaseScope, ScopeResolverMixin):
    def __init__(self, name: str, lock: Optional[RLock] = None):
        super().__init__(name)
        self._lock: RLock = lock or RLock()

    def has_rule(self, name: str) -> bool:
        try:
            self._resolve_rule(name)
            return True
        except RuleNotFoundException:
            return False
    
    def get_rule(self, name: str) -> Rule:
        return self._resolve_rule(name)

    def add_rule(self, name: str, rule: Rule):
        with self._lock:
            scope, rule_name = self._resolve_path(name)
            scope._rules[rule_name] = rule

    def remove_rule(self, name: str):
        with self._lock:
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
        with self._lock:
            parent_scope, child_name = self._resolve_path(name)
            parent_scope._children[child_name] = scope
            scope._parent = parent_scope

    def remove_scope(self, name: str):
        with self._lock:
            parent_scope, child_name = self._resolve_path(name)
            if child_name not in parent_scope._children:
                raise ScopeNotFoundException(f"Scope '{child_name}' not found")
            del parent_scope._children[child_name]

    def call(self, name: str, *args, **kwargs):
        rule = self._resolve_rule(name)
        return rule(*args, **kwargs)

class AsyncScope(BaseScope, ScopeResolverMixin):
    def __init__(self, name: str, lock: Optional[Lock] = None):
        super().__init__(name)
        self._lock: Lock = lock or Lock()

    async def has_rule(self, name: str) -> bool:
        try:
            self._resolve_rule(name)
            return True
        except RuleNotFoundException:
            return False

    async def get_rule(self, name: str) -> Rule:
        return self._resolve_rule(name)

    async def add_rule(self, name: str, rule: Rule):
        async with self._lock:
            scope, rule_name = self._resolve_path(name)
            scope._rules[rule_name] = rule

    async def remove_rule(self, name: str):
        async with self._lock:
            scope, rule_name = self._resolve_path(name)
            if rule_name not in scope._rules:
                raise RuleNotFoundException(f"Rule '{rule_name}' not found")
            del scope._rules[rule_name]

    async def has_scope(self, name: str) -> bool:
        try:
            self._resolve_scope(name)
            return True
        except ScopeNotFoundException:
            return False

    async def get_scope(self, name: str) -> "AsyncScope":
        return self._resolve_scope(name)

    async def add_scope(self, name: str, scope: "AsyncScope"):
        async with self._lock:
            parent_scope, child_name = self._resolve_path(name)
            parent_scope._children[child_name] = scope
            scope._parent = parent_scope

    async def remove_scope(self, name: str):
        async with self._lock:
            parent_scope, child_name = self._resolve_path(name)
            if child_name not in parent_scope._children:
                raise ScopeNotFoundException(f"Scope '{child_name}' not found")
            del parent_scope._children[child_name]

    async def call(self, name: str, *args, **kwargs):
        rule = self._resolve_rule(name)
        result = rule(*args, **kwargs)
        if inspect.isawaitable(result):
            result = await result
        return result