from pytest import fixture, raises
from lib import education


@fixture
def client_mock(mocker):
    return mocker.patch("lib.education.boto3.client")


@fixture
def data_response():
    return {
        "Items": [
            {"sk": {"S": "edu#0#name"}, "text": {"S": "Pitt"}},
            {"sk": {"S": "edu#0#location"}, "text": {"S": "Pittsburgh, PA"}},
            {
                "sk": {"S": "edu#0#achievement#0"},
                "text": {"S": "Bachelor in yolo"},
            },
        ]
    }


@fixture
def data_response_no_achievement_index():
    return {
        "Items": [
            {"sk": {"S": "edu#0#name"}, "text": {"S": "Pitt"}},
            {"sk": {"S": "edu#0#location"}, "text": {"S": "Pittsburgh, PA"}},
            {
                "sk": {"S": "edu#0#achievement"},
                "text": {"S": "Bachelor in yolo"},
            },
        ]
    }


def test_build(client_mock, data_response, session_data, table_name):
    client_mock.return_value.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.return_value.query.return_value = data_response
    observed = education.build(table_name, session_data)
    assert observed["statusCode"] == 200
    assert observed["headers"] == {"Content-Type": "text/html"}


def test_build_no_achievement_index(
    client_mock, data_response_no_achievement_index, session_data, table_name
):
    client_mock.return_value.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.return_value.query.return_value = data_response_no_achievement_index
    with raises(ValueError):
        education.build(table_name, session_data)


def test_act():
    data, events = education.act("yolo", {}, {})
    assert data == {}
