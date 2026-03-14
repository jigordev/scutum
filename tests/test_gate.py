import pytest
from scutum.gate import Gate
from scutum.policy import Policy
from scutum.response import Response
from scutum.exceptions import AuthorizationException

@pytest.fixture
def gate():
    return Gate()

class User:
    def __init__(self, id, is_admin=False):
        self.id = id
        self.is_admin = is_admin

class Post:
    def __init__(self, id, author_id):
        self.id = id
        self.author_id = author_id

def test_gate_rule(gate):
    @gate.rule("edit")
    def edit_post(user, post):
        return user.id == post.author_id

    user = User(1)
    post = Post(1, 1)
    other_post = Post(2, 2)

    assert gate.allowed("edit", user, post) is True
    assert gate.denied("edit", user, post) is False
    assert gate.allowed("edit", user, other_post) is False

def test_gate_policy_class(gate):
    @gate.policy("post")
    class PostPolicy(Policy):
        def edit(self, user, post):
            return user.id == post.author_id

    user = User(1)
    post = Post(1, 1)

    assert gate.allowed("post:edit", user, post) is True
    assert gate.check("post:edit", user, post) is True

def test_gate_policy_instance(gate):
    class Service:
        def get_auth_status(self, user):
            return user.is_admin

    class UserPolicy(Policy):
        def __init__(self, service):
            self.service = service
            
        def create(self, user):
            return self.service.get_auth_status(user)
            
    policy_instance = UserPolicy(Service())
    gate.add_policy("user", policy_instance)

    admin = User(1, is_admin=True)
    normal = User(2, is_admin=False)

    assert gate.allowed("user:create", admin) is True
    assert gate.allowed("user:create", normal) is False

def test_gate_authorize_raises_exception(gate):
    @gate.rule("view")
    def view_post(user):
        return Response.deny("Custom denial", 401)
        
    user = User(1)
    with pytest.raises(AuthorizationException) as exc:
        gate.authorize("view", user)
    
    assert exc.value.status_code == 401
    assert str(exc.value) == "Custom denial"
