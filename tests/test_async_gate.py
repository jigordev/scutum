import pytest
import asyncio
from scutum.gate import AsyncGate
from scutum.policy import AsyncPolicy
from scutum.response import Response

@pytest.fixture
def gate():
    return AsyncGate()

class User:
    def __init__(self, id, is_admin=False):
        self.id = id
        self.is_admin = is_admin

@pytest.mark.asyncio
async def test_async_gate_rule(gate):
    @gate.rule("edit")
    async def edit_post(user, post_id: int):
        await asyncio.sleep(0.01)
        return user.id == post_id

    user = User(1)
    
    # Needs to wait for check because setup gathers rules
    assert await gate.allowed("edit", user, 1) is True
    assert await gate.allowed("edit", user, 2) is False

@pytest.mark.asyncio
async def test_async_gate_late_registration(gate):
    @gate.rule("first")
    async def first_rule(user):
        return True
        
    # First check triggers setup
    assert await gate.allowed("first", User(1)) is True
    
    # Registering rule AFTER setup
    @gate.rule("second")
    async def second_rule(user):
        return False
        
    # It should register automatically because we fixed the late-registration bug
    assert await gate.allowed("second", User(1)) is False

@pytest.mark.asyncio
async def test_async_policy_instance(gate):
    class Service:
        async def verify(self, user):
            await asyncio.sleep(0.01)
            return user.is_admin
            
    class UserPolicy(AsyncPolicy):
        def __init__(self, service):
            self.service = service
            
        async def delete(self, user):
            return await self.service.verify(user)
            
    service = Service()
    policy = UserPolicy(service)
    
    # Manual registration instead of decorator
    await gate.add_policy("user", policy)
    
    assert await gate.allowed("user:delete", User(1, is_admin=True)) is True
    assert await gate.allowed("user:delete", User(2, is_admin=False)) is False
