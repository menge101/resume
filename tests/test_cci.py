from pytest import fixture, raises
from lib import cci


@fixture
def client_mock(mocker):
    return mocker.patch("lib.experience.boto3.client")


@fixture
def data_response():
    return {
        "Items": [
            {"sk": {"S": "cci#0#name"}, "text": {"S": "Cert1"}},
            {"sk": {"S": "cci#1#name"}, "text": {"S": "Thing"}},
            {"sk": {"S": "cci#1#start-month"}, "text": {"S": "February"}},
            {"sk": {"S": "cci#1#start-year"}, "text": {"S": "2022"}},
            {"sk": {"S": "cci#1#end-year"}, "text": {"S": "2025"}},
            {"sk": {"S": "cci#1#end-month"}, "text": {"S": "January"}},
            {"sk": {"S": "cci#1#title"}, "text": {"S": "Title"}},
            {
                "sk": {"S": "cci#1#achievement#0"},
                "text": {"S": "Grew the group from 0 to over 700 members"},
            },
            {
                "sk": {"S": "cci#1#achievement#1"},
                "text": {
                    "S": "Built the group's website using AWS Amplify and JavaScript"
                },
            },
        ]
    }


@fixture
def invalid_achievement_response():
    return {
        "Items": [
            {
                "sk": {"S": "cci#1#achievement"},
                "text": {"S": "Grew the group from 0 to over 700 members"},
            },
        ]
    }


@fixture
def invalid_title_response():
    return {
        "Items": [
            {"sk": {"S": "cci#0#name"}, "text": {"S": "Cert1"}},
            {"sk": {"S": "cci#1#start-month"}, "text": {"S": "February"}},
            {"sk": {"S": "cci#1#start-year"}, "text": {"S": "2022"}},
            {"sk": {"S": "cci#1#end-year"}, "text": {"S": "2025"}},
            {"sk": {"S": "cci#1#end-month"}, "text": {"S": "January"}},
            {"sk": {"S": "cci#1#title"}, "text": {"S": "Title"}},
            {
                "sk": {"S": "cci#1#achievement#0"},
                "text": {"S": "Grew the group from 0 to over 700 members"},
            },
            {
                "sk": {"S": "cci#1#achievement#1"},
                "text": {
                    "S": "Built the group's website using AWS Amplify and JavaScript"
                },
            },
        ]
    }


def test_build(client_mock, data_response, session_data, table_name):
    client_mock.return_value.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.return_value.query.return_value = data_response
    observed = cci.build(table_name, session_data)
    assert observed["headers"] == {"Content-Type": "text/html"}
    assert observed["statusCode"] == 200


def test_invalid_achievement(
    client_mock, invalid_achievement_response, session_data, table_name
):
    client_mock.return_value.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.return_value.query.return_value = invalid_achievement_response
    with raises(ValueError):
        cci.build(table_name, session_data)


def test_invalid_cci(client_mock, invalid_title_response, session_data, table_name):
    client_mock.return_value.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.return_value.query.return_value = invalid_title_response
    with raises(AttributeError):
        cci.build(table_name, session_data)


def test_act():
    data, events = cci.act("yolo", {}, {})
    assert data == {}
