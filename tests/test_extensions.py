import pytest
import asyncio
from flask import Flask
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient as FastAPITestClient

from scutum.gate import Gate, AsyncGate
from scutum.ext.flask import Scutum
from scutum.ext.fastapi import fastapi_adapter
from scutum.exceptions import AuthorizationException

# --- Flask Tests ---

def test_flask_extension():
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Mock user context
    current_user = {"id": 1, "is_admin": False}
    
    def get_user():
        return current_user
        
    scutum = Scutum(app, user_resolver=get_user)
    gate = scutum.gate
    
    @gate.rule("view_dashboard")
    def can_view_dashboard(user):
        return user.get("is_admin", False)
        
    @gate.rule("edit_post")
    def can_edit_post(user, post_id: int):
        return user.get("id") == post_id
        
    @app.route("/dashboard")
    @scutum.authorized("view_dashboard")
    def dashboard():
        return "Dashboard OK"
        
    @app.route("/post/<int:post_id>")
    @scutum.authorized("edit_post")
    def edit_post(post_id):
        return f"Post {post_id} OK"

    @app.errorhandler(AuthorizationException)
    def handle_auth_error(e):
        return str(e), e.status_code

    client = app.test_client()
    
    # Normal user viewing dashboard -> 403
    response = client.get("/dashboard")
    assert response.status_code == 403
    
    # Normal user editing their post -> 200 (post_id matching user_id)
    response = client.get("/post/1")
    assert response.status_code == 200
    assert response.data.decode() == "Post 1 OK"
    
    # Normal user editing someone else's post -> 403
    response = client.get("/post/2")
    assert response.status_code == 403
    
    # Admin viewing dashboard
    current_user = {"id": 2, "is_admin": True}
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert response.data.decode() == "Dashboard OK"


# --- FastAPI Tests ---

def test_fastapi_extension():
    app = FastAPI()
    gate = AsyncGate()
    
    current_user = {"id": 1, "is_admin": False}
    
    async def get_current_user():
        return current_user
        
    fastapi_gate = fastapi_adapter(gate, default_user_resolver=get_current_user)
    
    @gate.rule("delete_user")
    async def can_delete_user(user, target_id: int):
        return user.get("is_admin") or user.get("id") == target_id

    # FastAPI route using dependency
    @app.delete("/users/{target_id}")
    async def delete_user(
        target_id: int, 
        user = Depends(fastapi_gate.can("delete_user", resource_resolver=lambda request, target_id=None: target_id))
    ):
        return {"status": "deleted"}

    client = FastAPITestClient(app)
    
    # User 1 deleting User 2 -> 403
    response = client.delete("/users/2")
    assert response.status_code == 403
    
    # User 1 deleting User 1 -> 200
    response = client.delete("/users/1")
    assert response.status_code == 200
    
    # Admin deleting User 2 -> 200
    current_user["is_admin"] = True
    response = client.delete("/users/2")
    assert response.status_code == 200
