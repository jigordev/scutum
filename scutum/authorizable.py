from scutum.gate import Gate

class Authorizable:
    def __init__(self, gate: Gate):
        self.gate = gate

    def can(self, action: str, *args, **kwargs):
        return self.gate.allowed(action, self, *args, **kwargs)
    
    def cannot(self, action: str, *args, **kwargs):
        return self.gate.denied(action, self, *args, **kwargs)