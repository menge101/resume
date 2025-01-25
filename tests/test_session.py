from datetime import datetime
from pytest import fixture, raises
from lib import session


@fixture
def boto3_mock(mocker):
    return mocker.patch("lib.session.boto3")


@fixture
def client_mock(boto3_mock):
    return boto3_mock.client.return_value


@fixture
def base_time():
    return datetime(year=2024, month=1, day=1, hour=0, minute=0, second=0)


@fixture
def event_with_cookie(session_id):
    return {"cookies": [f"id_={session_id}"]}


@fixture
def invalid_session_data():
    return {"yo": "lo"}


@fixture
def session_data_none():
    return {}


@fixture
def session_data(base_time, session_id):
    return {"id_": session_id, "ttl": base_time.timestamp()}


@fixture
def table_mock(boto3_mock, mocker):
    tbl_mock = boto3_mock.resource.return_value.Table = mocker.Mock(name="Table")
    return tbl_mock


def test_build_no_session(client_mock, mocker, session_data_none, table_name):
    mocker.patch("lib.session.cookie.expiration_time", return_value=0)
    mocker.patch("lib.session.cookie.expiration_as_ttl", return_value="0")
    mocker.patch("lib.session.uuid1", return_value="1")
    with raises(ValueError):
        session.build(table_name, session_data_none)


def test_build_with_session(
    base_time, client_mock, mocker, session_id, session_data, table_name
):
    mocker.patch(
        "lib.session.cookie.expiration_as_ttl", return_value=base_time.timestamp()
    )
    observed = session.build(table_name, session_data)
    expected = {
        "body": "",
        "cookies": [
            f"id_={session_id}; Expires=Mon, 01 Jan 2024 00:00:00 GMT; HttpOnly; Secure; SameSite=Strict"
        ],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected


def test_cookie_crumble(event_with_cookie, session_id):
    observed = session.get_session_id_from_cookies(event_with_cookie)
    expected = session_id
    assert observed == expected


def test_handle_session(event_with_cookie, session_id, table_mock, table_name):
    table_mock.return_value.get_item.return_value = {"Item": {"id_": session_id}}
    observed = session.handle_session(event_with_cookie, table_name)
    expected = {"id_": session_id}
    assert observed == expected


def test_act_no_session(boto3_mock, mocker, session_data_none, table_name):
    mocker.patch(
        "lib.session.cookie.expiration_time", return_value=datetime.fromtimestamp(0)
    )
    mocker.patch("lib.session.uuid1", return_value="1")
    ddb_tbl_mock = boto3_mock.resource.return_value.Table
    ddb_tbl_mock.return_value = mocker.Mock(name="Table()")
    observed = session.act(table_name, session_data_none, {})
    expected = (
        {
            "id_": "1",
            "pk": "session",
            "sk": "1",
            "translate": {"local": "en", "state": "closed"},
            "ttl": "0",
        },
        ["session-created"],
    )
    ddb_tbl_mock.return_value.put_item.assert_called()
    assert observed == expected


def test_act_with_session(boto3_mock, mocker, session_data, table_mock, table_name):
    mocker.patch(
        "lib.session.cookie.expiration_time", return_value=datetime.fromtimestamp(0)
    )
    mocker.patch("lib.session.uuid1", return_value="1")
    ddb_tbl_mock = boto3_mock.resource.return_value.Table
    ddb_tbl_mock.return_value = mocker.Mock(name="Table()")
    observed = session.act(table_name, session_data, {})
    ddb_tbl_mock.return_value.put_item.assert_not_called()
    assert observed == (session_data, [])


def test_build_with_invalid_session(
    boto3_mock, mocker, invalid_session_data, table_mock, table_name
):
    mocker.patch(
        "lib.session.cookie.expiration_time", return_value=datetime.fromtimestamp(0)
    )
    mocker.patch("lib.session.uuid1", return_value="1")
    ddb_tbl_mock = boto3_mock.resource.return_value.Table
    ddb_tbl_mock.return_value = mocker.Mock(name="Table()")
    with raises(ValueError):
        session.build(table_name, invalid_session_data, {})


def test_update_session_raises_client_error(
    boto3_mock, mocker, session_data, table_mock, table_name
):
    class MockException(Exception):
        pass

    mocker.patch("lib.session.botocore.exceptions.ClientError", MockException)
    table_mock.return_value.put_item.side_effect = MockException()
    with raises(ValueError):
        session.update_session(table_name, session_data)
