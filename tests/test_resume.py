from lib import resume
from pytest import fixture, raises


@fixture
def context(mocker):
    return mocker.Mock(name="context")


@fixture
def event():
    return {}


@fixture
def table(mocker):
    mocker.patch("lib.resume.os.getenv", return_value="testing")


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
    }
    observed = resume.handler(event, context)
    assert observed == expected


def test_resume_exception(context, event, mocker, table):
    mocker.patch("lib.resume.dispatch", side_effect=Exception)
    expected = {
        "body": "<div>\nError: \n</div>",
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 500,
    }
    observed = resume.handler(event, context)
    assert observed == expected


def test_resume_no_table(context, event):
    with raises(ValueError):
        resume.handler(event, context)


def test_build():
    assert resume.build("yolo")
