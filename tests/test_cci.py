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
    expected = (
        '<div class="cci"><span class="heading">yolo</span><div><div class="cci"><ul><li><span class="name">'
        'Cert1</span></li></ul></div><div class="cci"><ul><li><span class="name">Thing</span>&nbsp;&nbsp;&#183;'
        '&nbsp;&nbsp;<span class="dates">February 2022 - January 2025</span></li><li class="cci"><span class='
        '"title">Title</span></li><li><ul class="bullets"><li class="bullets">Grew the group from 0 to over 700'
        ' members</li><li class="bullets">Built the group&#x27;s website using AWS Amplify and JavaScript</li>'
        "</ul></li></ul></div></div></div>"
    )
    assert observed == expected


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
