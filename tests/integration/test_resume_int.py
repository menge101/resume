from pytest import fixture
from lib import resume


@fixture
def event_no_cookie():
    return {}


@fixture
def event_with_cookie(session_id):
    return {"cookies": [f"id_={session_id}"]}


@fixture
def session(resource, session_id, table):
    tbl = resource.Table(table)
    tbl.put_item(
        Item={"pk": "session", "sk": session_id, "id_": session_id, "local": "en"}
    )
    return session_id


def test_handle_session_no_session(event_no_cookie, table):
    observed = resume.handle_session(event_no_cookie, table)
    expected = {"local": "en", "id_": None}
    assert observed == expected


def test_handle_session(event_with_cookie, session, table):
    observed = resume.handle_session(event_with_cookie, table)
    expected = {"pk": "session", "sk": session, "local": "en", "id_": session}
    assert observed == expected
