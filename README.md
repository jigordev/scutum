# Scutum

Scutum is a lightweight authorization library inspired by Laravel's Policies and Gates. It provides an easy way to manage permissions using decorators, making access control more structured and maintainable.

## Installation

```sh
pip install scutum
```

## Quick Start

### Basic Usage

```python
from scutum import Gate, Policy

# Create a gate instance
gate = Gate()

# Define a simple rule
@gate.rule("edit_post")
def edit_post(user, post):
    return user.id == post.author_id

# Check permissions
if gate.allowed("edit_post", user, post):
    print("User can edit this post")
```

### Async Support

```python
from scutum import AsyncGate, AsyncPolicy
import asyncio

# Create an async gate
gate = AsyncGate()

# Define async rules
@gate.rule("delete_user")
async def can_delete_user(user, target_id: int):
    await asyncio.sleep(0.01)  # Simulate async operation
    return user.is_admin or user.id == target_id

# Use in async context
async def check_permission():
    return await gate.allowed("delete_user", user, 2)
```

## Usage

### Defining Rules

Rules are individual permission checks that can be registered with the gate.

```python
from scutum import Gate

gate = Gate()

@gate.rule("edit_post")
def edit_post(user, post):
    return user.id == post.author_id

@gate.rule("delete_user")
def delete_user(user, target_id: int):
    return user.is_admin or user.id == target_id
```

### Defining Policies

Policies are classes that group related rules together.

#### Policy Classes

```python
from scutum import Policy, Gate

gate = Gate()

@gate.policy("post")
class PostPolicy(Policy):
    def edit(self, user, post):
        return user.id == post.author_id
    
    def delete(self, user, post):
        return user.id == post.author_id or user.is_admin
```

#### Policy Instances

```python
from scutum import Policy, Gate

class Service:
    def get_auth_status(self, user):
        return user.is_admin

class UserPolicy(Policy):
    def __init__(self, service):
        self.service = service
    
    def create(self, user):
        return self.service.get_auth_status(user)

gate = Gate()
service = Service()
policy_instance = UserPolicy(service)
gate.add_policy("user", policy_instance)
```

#### Async Policies

```python
from scutum import AsyncPolicy, AsyncGate

class Service:
    async def verify(self, user):
        await asyncio.sleep(0.01)
        return user.is_admin

class UserPolicy(AsyncPolicy):
    def __init__(self, service):
        self.service = service
    
    async def delete(self, user):
        return await self.service.verify(user)

gate = AsyncGate()
service = Service()
policy = UserPolicy(service)
await gate.add_policy("user", policy)
```

### Checking Permissions

```python
from scutum import Gate, Policy

@gate.policy("user")
class UserPolicy(Policy):
    def create(self, user):
        return user.is_admin
    
    def delete(self, user):
        return user.is_admin

def create_user():
    user = current_user()

    if gate.allowed("user:create", user):  # If action is allowed
        return "You are authorized to create a user"

    if gate.denied("user:create", user):  # If action is denied
        return "You are not authorized to create a user"

    if gate.any(["user:create", "user:delete"], user):  # If any action
        return "You have permission to create or delete a user."

    if gate.none(["user:create", "user:delete"], user):  # If none action
        return "You do not have permission to create or delete a user."

    response = gate.check("user:create", user)  # bool or Response
    
    return response
```

### Responses

Responses are classes that can be returned within an action or policy for an allowed or denied action and can define details such as status code and response body.

```python
from scutum import Response, Gate

gate = Gate()

@gate.rule("update_user")
def update_user(authenticated_user, user):
    if authenticated_user.is_admin:
        return Response.allow("User authorized")

    return Response.deny("This action is not authorized", 401)
```

## Framework Integrations

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from scutum import AsyncGate
from scutum.ext.fastapi import fastapi_adapter

app = FastAPI()
gate = AsyncGate()

# Define user resolver
async def get_current_user():
    return {"id": 1, "is_admin": False}

# Create FastAPI adapter
fastapi_gate = fastapi_adapter(gate, default_user_resolver=get_current_user)

# Define rules
@gate.rule("delete_user")
async def can_delete_user(user, target_id: int):
    return user.get("is_admin") or user.get("id") == target_id

# Use in routes
@app.delete("/users/{target_id}")
async def delete_user(
    target_id: int,
    user = Depends(fastapi_gate.can("delete_user", resource_resolver=lambda request, target_id=None: target_id))
):
    return {"status": "deleted"}
```

### Flask Integration

```python
from flask import Flask
from scutum import Gate
from scutum.ext.flask import Scutum

app = Flask(__name__)

# Mock user context
current_user = {"id": 1, "is_admin": False}

def get_user():
    return current_user

# Initialize Flask extension
scutum = Scutum(app, user_resolver=get_user)
gate = scutum.gate

# Define rules
@gate.rule("view_dashboard")
def can_view_dashboard(user):
    return user.get("is_admin", False)

# Use in routes
@app.route("/dashboard")
@scutum.authorized("view_dashboard")
def dashboard():
    return "Dashboard OK"
```

## Development

### Running Tests

```sh
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### Dependencies

- **pytest-asyncio** - Required for async test support
- **FastAPI** - For FastAPI integration examples
- **Flask** - For Flask integration examples

## Extensions

You can explore example projects demonstrating how to integrate this library with popular Python web frameworks:

* **Flask Example**: [github.com/jigordev/flask-scutum-example](https://github.com/jigordev/flask-scutum-example)
* **FastAPI Example**: [github.com/jigordev/fastapi-scutum-example](https://github.com/jigordev/fastapi-scutum-example)

## License

MIT License
