def authorizable(cls, gate):
    def can(self, action: str, *args, **kwargs):
        return gate.allowed(action, self, *args, **kwargs)
    
    def cannot(self, action: str, *args, **kwargs):
        return gate.denied(action, self, *args, **kwargs)
    
    cls.can = can
    cls.cannot = cannot
    return cls