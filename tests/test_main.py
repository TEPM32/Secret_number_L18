import os
import pytest
from main import app, db, index

@pytest.fixture()
def client():
    app.config("TESTING")=True
    os.environ("DATABASE_URL") ="sqlite:///:memory:"
    client = app.test_client()

    # clean up before every teste
    cleanup()
    db.create_all()
    yield client

def cleanup():
    # clean up the database
    db.drop_all()
