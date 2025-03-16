# Thyros

Thyros is a lightweight authorization library inspired by Laravel's Policies and Gates. It provides an easy way to manage permissions using decorators, making access control more structured and maintainable.

## Installation

```sh
pip install thyros
```

## Usage

### Defining Actions

An action is a set of rules that determine whether a user can manipulate a particular resource.

```python
from thyros import gate

@gate.register("edit")
def edit_post(user, post):
    return user.id == post.author_id
```

### Defining Policies

A policy is a named class whose methods are actions that will be registered along with the class name.

```python
from thyros import Policy, gate

@gate.policy("user")
class UserPolicy(Policy)
    def create(self, user, *args, **kwargs)
        return user.is_admin
```

### Checking Permissions

Through the guard it is possible to check the permissions of registered policies.

```python
from thyros import Policy, gate

@gate.policy("user")
class UserPolicy(Policy)
    def create(self, user, *args, **kwargs)
        return user.is_admin

    def delete(self, user, *args, **kwargs)
        return user.is_admin

def create_user():
    user = current_user()

    if guard.allowed("user:create", user): # If action is allowed
        return "You are authorized to create a user"

    if guard.denied("user:create", user): # If action is denied
        return "You are not authorized to create a user"

    if guard.any(["user:create", "user:delete"], user): # If any action
        return "You have permission to create or delete a user."

    if guard.none(["user:create", "user:delete"], user): # If none action
        return "You do not have permission to create or delete a user."

    response = guard.check("user:create", user) # bool or Response
    
    return response
```

### Responses

Responses are classes that can be returned within an action or policy for an allowed or denied action and can define details such as status code and response body.

```python
from thyros import Response, gate

@guard.register("update")
def update_user(authenticated_user, user)
    if authenticated_user.is_admin:
        return Response.allow("User authorized")

    return Response.deny("This action is not authorized")
```

## License

MIT License