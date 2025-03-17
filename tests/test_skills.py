from pytest import fixture
from lib import skills


@fixture
def client_mock(mocker):
    return mocker.Mock(name="client")


@fixture
def data_response():
    return {
        "Items": [
            {"text": {"S": "skill1"}},
            {"text": {"S": "skill2"}},
            {"text": {"S": "skill3"}},
        ]
    }


@fixture
def mock_connection_thread(client_mock, mocker, table_name):
    thread = mocker.Mock(name="thread")
    thread.join.return_value = (table_name, client_mock, mocker.Mock(name="resource"))
    return thread


def test_build(client_mock, data_response, mock_connection_thread, session_data, table_name):
    client_mock.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.query.return_value = data_response
    observed = skills.build(mock_connection_thread, session_data)
    assert observed["statusCode"] == 200
    assert observed["headers"] == {"Content-Type": "text/html"}


def test_act(mock_connection_thread):
    data, events = skills.act("yolo", {}, {})
    assert data == {}
