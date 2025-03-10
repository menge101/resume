from pytest import fixture
from lib import skills


@fixture
def client_mock(mocker):
    return mocker.patch("lib.skills.boto3.client")


@fixture
def data_response():
    return {
        "Items": [
            {"text": {"S": "skill1"}},
            {"text": {"S": "skill2"}},
            {"text": {"S": "skill3"}},
        ]
    }


def test_build(client_mock, data_response, session_data, table_name):
    client_mock.return_value.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.return_value.query.return_value = data_response
    observed = skills.build(table_name, session_data)
    assert observed["statusCode"] == 200
    assert observed["headers"] == {"Content-Type": "text/html"}


def test_act():
    data, events = skills.act("yolo", {}, {})
    assert data == {}
