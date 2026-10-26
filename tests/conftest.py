"""Shared fixture: a seeded file DB with a guarded read connection.

The read connection and the admin connection point at the same temp
file, so the authorizer-guarded reads see the seeded synthetic data.
"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from portfolio_risk_agent.db import connect_admin, connect_read, create_schema
from portfolio_risk_agent.seed import seed
from portfolio_risk_agent.agent import Agent


@pytest.fixture()
def store():
    tmp = tempfile.TemporaryDirectory()
    path = os.path.join(tmp.name, "test.db")
    admin = connect_admin(path)
    create_schema(admin)
    seed(admin)
    read_con = connect_read(path)
    yield {"admin": admin, "read": read_con, "path": path, "tmp": tmp}
    read_con.close()
    admin.close()
    tmp.cleanup()


@pytest.fixture()
def agent(store):
    return Agent(store["read"], store["admin"])
