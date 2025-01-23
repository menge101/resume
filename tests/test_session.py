from pytest import fixture


from lib import session


@fixture
def boto3_mock(mocker):
    return mocker.patch("lib.session.boto3")


@fixture
def client_mock(boto3_mock):
    return boto3_mock.client.return_value


@fixture
def session_data_none():
    return {"id_": None}


@fixture
def session_data(session_id):
    return {"id_": session_id}


def test_build_no_session(client_mock, mocker, session_data_none, table_name):
    mocker.patch("lib.session.cookie.expiration_time", return_value=0)
    mocker.patch("lib.session.cookie.expiration_as_ttl", return_value="0")
    mocker.patch("lib.session.uuid1", return_value="1")
    observed = session.build(table_name, session_data_none)
    expected = {
        "body": "",
        "cookies": ["id_=1; HttpOnly; Secure"],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected


def test_build_with_session(client_mock, mocker, session_id, session_data, table_name):
    mocker.patch("lib.session.cookie.expiration_as_ttl", return_value=0)
    observed = session.build(table_name, session_data)
    expected = {
        "body": "",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 204,
    }
    assert observed == expected
