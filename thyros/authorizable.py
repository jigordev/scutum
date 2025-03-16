class Authorizable:
    def can(self, action: str, *args, **kwargs):
        from thyros.gate import gate
        return gate.allowed(action, self, *args, **kwargs)
    
    def cannot(self, action: str, *args, **kwargs):
        from thyros.gate import gate
        return gate.denied(action, self, *args, **kwargs)