from lib import resume
from pytest import fixture


@fixture
def boto3_mock(mocker):
    return mocker.patch("lib.resume.boto3")


@fixture
def context(mocker):
    return mocker.Mock(name="context")


@fixture
def event():
    return {}


@fixture
def event_with_cookie(session_id):
    return {"cookies": [f"id_={session_id}"]}


@fixture
def table(mocker):
    mocker.patch("lib.resume.os.environ", {"ddb_table_name": "testing"})


@fixture
def table_mock(boto3_mock, mocker):
    tbl_mock = boto3_mock.resource.return_value.Table = mocker.Mock(name="Table")
    return tbl_mock


def test_resume(context, event, mocker, table):
    mocker.patch("lib.resume.dispatch", return_value=True)
    assert resume.handler(event, context)


def test_resume_error(context, event, mocker, table):
    mocker.patch("lib.resume.dispatch", side_effect=ValueError)
    expected = {
        "body": "<div>\nError: \n</div>",
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 400,
        "cookies": [],
    }
    observed = resume.handler(event, context)
    assert observed == expected


def test_resume_exception(context, event, mocker, table):
    mocker.patch("lib.resume.dispatch", side_effect=Exception)
    expected = {
        "body": "<div>\nError: \n</div>",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 500,
    }
    observed = resume.handler(event, context)
    assert observed == expected


def test_resume_no_table(context, event):
    observed = resume.handler(event, context)
    expected = {
        "body": "<div>\nError: Missing environment variable 'ddb_table_name'\n</div>",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 500,
    }
    assert observed == expected


def test_cookie_crumble(event_with_cookie, session_id):
    observed = resume.cookie_crumble(event_with_cookie)
    expected = session_id
    assert observed == expected


def test_handle_session(event_with_cookie, session_id, table_mock, table_name):
    table_mock.return_value.get_item.return_value = {"Item": {"id_": session_id}}
    observed = resume.handle_session(event_with_cookie, table_name)
    expected = {"id_": session_id}
    assert observed == expected
