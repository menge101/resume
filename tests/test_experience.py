from pytest import fixture, raises
from lib import experience


@fixture
def client_mock(data_response, mocker):
    return mocker.Mock(name="client")


@fixture
def connection_thread_mock(client_mock, mocker, table_name):
    t = mocker.Mock(name="thread")
    t.join.return_value = table_name, client_mock, mocker.Mock(name="resource")
    return t


@fixture
def data_response():
    return {
        "Items": [
            {"sk": {"S": "exp#0#name"}, "text": {"S": "UPMC Enterprises"}},
            {"sk": {"S": "exp#0#start#month"}, "text": {"S": "February"}},
            {"sk": {"S": "exp#0#start#year"}, "text": {"S": "2022"}},
            {"sk": {"S": "exp#0#end#year"}, "text": {"S": "2025"}},
            {"sk": {"S": "exp#0#end#month"}, "text": {"S": "January"}},
            {
                "sk": {"S": "exp#0#title"},
                "text": {"S": "Senior Cloud Infrastructure Engineer"},
            },
            {"sk": {"S": "exp#0#location"}, "text": {"S": "Pittsburgh, PA"}},
            {
                "sk": {"S": "exp#0#bullet#0"},
                "text": {"S": "Implemented an event driven security remediation system "},
            },
            {"sk": {"S": "exp#0#bullet#1"}, "text": {"S": "yo"}},
            {"sk": {"S": "exp#0#bullet#2"}, "text": {"S": "Lo"}},
        ]
    }


@fixture
def data_response_no_end():
    return {
        "Items": [
            {"sk": {"S": "exp#0#name"}, "text": {"S": "UPMC Enterprises"}},
            {"sk": {"S": "exp#0#start#month"}, "text": {"S": "February"}},
            {"sk": {"S": "exp#0#start#year"}, "text": {"S": "2022"}},
            {
                "sk": {"S": "exp#0#title"},
                "text": {"S": "Senior Cloud Infrastructure Engineer"},
            },
            {"sk": {"S": "exp#0#location"}, "text": {"S": "Pittsburgh, PA"}},
            {
                "sk": {"S": "exp#0#bullet#0"},
                "text": {"S": "Implemented an event driven security remediation system "},
            },
            {"sk": {"S": "exp#0#bullet#1"}, "text": {"S": "yo"}},
            {"sk": {"S": "exp#0#bullet#2"}, "text": {"S": "Lo"}},
        ]
    }


@fixture
def data_response_bullet_no_index():
    return {
        "Items": [
            {"sk": {"S": "exp#0#name"}, "text": {"S": "UPMC Enterprises"}},
            {"sk": {"S": "exp#0#start#month"}, "text": {"S": "February"}},
            {"sk": {"S": "exp#0#start#year"}, "text": {"S": "2022"}},
            {"sk": {"S": "exp#0#end#year"}, "text": {"S": "2025"}},
            {"sk": {"S": "exp#0#end#month"}, "text": {"S": "January"}},
            {
                "sk": {"S": "exp#0#title"},
                "text": {"S": "Senior Cloud Infrastructure Engineer"},
            },
            {"sk": {"S": "exp#0#location"}, "text": {"S": "Pittsburgh, PA"}},
            {
                "sk": {"S": "exp#0#bullet"},
                "text": {"S": "Implemented an event driven security remediation system "},
            },
        ]
    }


def test_build(client_mock, connection_thread_mock, data_response, session_data):
    client_mock.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.query.return_value = data_response
    observed = experience.build(connection_thread_mock, session_data)
    assert observed["statusCode"] == 200
    assert observed["headers"] == {"Content-Type": "text/html"}


def test_build_no_end(client_mock, connection_thread_mock, data_response_no_end, session_data):
    client_mock.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.query.return_value = data_response_no_end
    observed = experience.build(connection_thread_mock, session_data)
    expected = (
        '<div hx-get="/ui/experience" hx-swap="outerHTML" '
        'hx-trigger="language-updated from:body" class="experience fade"><span '
        'class="bigger">yolo</span><ul class="job no-bullets '
        'no-break-print"><li><span class="name">UPMC Enterprises</span><span '
        'class="dates">&nbsp;&nbsp;&#183;&nbsp;&nbsp;February 2022 - '
        'Present</span></li><li class="title-and-loc">Senior Cloud Infrastructure '
        "Engineer&nbsp;&nbsp;&#183;&nbsp;&nbsp;Pittsburgh, PA</li><li><ul "
        'class="bullets"><li>Implemented an event driven security remediation system '
        "</li><li>yo</li><li>Lo</li></ul></li></ul></div>"
    )
    assert observed["body"] == expected


def test_build_no_bullet_index(
    client_mock,
    connection_thread_mock,
    data_response_bullet_no_index,
    session_data,
    table_name,
):
    client_mock.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.query.return_value = data_response_bullet_no_index
    with raises(ValueError):
        experience.build(connection_thread_mock, session_data)


def test_act(connection_thread_mock):
    data, events = experience.act(connection_thread_mock, {}, {})
    assert data == {}
