def _get_method(obj, method):
    def get_method(*args, **kwargs):
        return method(obj, *args, **kwargs)
    return get_method

class Policy:
    @classmethod
    def _to_actions(cls):
        obj = cls()

        actions = {}
        for name in dir(cls):
            value = getattr(cls, name)
            if callable(value) and not name.startswith("_"):
                actions[name] = _get_method(obj, value)
        return actions

    def view(self, user, *args, **kwargs):
        return True
    
    def view_many(self, user, *args, **kwargs):
        return True
    
    def create(self, user, *args, **kwargs):
        return True
    
    def update(self, user, *args, **kwargs):
        return True
    
    def delete(self, user, *args, **kwargs):
        return True
