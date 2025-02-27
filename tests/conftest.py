from pytest import fixture
import os


@fixture
def fake_data():
    return {
        "name": "Test Test",
        "city": "Townsville",
        "state": "St",
        "email": "person@server.yo",
        "github": "github.com/yolo",
    }


@fixture
def project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@fixture
def session_data(session_id):
    return {
        "local": "en",
        "id_": session_id,
        "sk": session_id,
        "translate": {"state": "closed"},
    }


@fixture
def session_id():
    return "1234567890"


@fixture
def table_name():
    return "test_table"
