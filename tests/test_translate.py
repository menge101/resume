from pytest import fixture, mark, raises
from lib import translate


@fixture
def boto3_mock(mocker):
    return mocker.patch("lib.translate.boto3")


@fixture
def boto3_session_mock(mocker):
    return mocker.patch("lib.translate.session.boto3")


@fixture
def client_mock(boto3_mock):
    return boto3_mock.client


@fixture
def resource_mock(boto3_mock):
    return boto3_mock.resource


def test_get_existing_data(client_mock, table_name):
    data = [
        {"sk": {"S": "eskay"}, "text": {"S": "yolo1"}},
        {"sk": {"S": "ska"}, "text": {"S": "yolo2"}},
    ]
    client_mock.query.return_value = {"Items": data}
    expected = {"eskay": "yolo1", "ska": "yolo2"}
    observed = translate.get_existing_en_data(client_mock, table_name)
    assert observed == expected


def test_act_open(boto3_mock, boto3_session_mock, session_data, session_id, table_name):
    params = {"action": "open"}
    observed = translate.act(table_name, session_data, params)
    expected = (
        {
            "id_": "1234567890",
            "local": "en",
            "sk": "1234567890",
            "translate": {"state": "open"},
        },
        [],
    )
    assert observed == expected


def test_act_choose(
    boto3_mock, boto3_session_mock, session_data, session_id, resource_mock, table_name
):
    resource_mock.Table.return_value.get_item.return_value = {
        "Item": {"languages": ["en, ne, fr, xx"]}
    }
    params = {"action": "FR"}
    expected = (
        {
            "id_": "1234567890",
            "local": "en",
            "sk": "1234567890",
            "translate": {"state": "closed"},
        },
        ["language-updated"],
    )
    observed = translate.act(table_name, session_data, params)
    assert observed == expected


@mark.parametrize("key_to_remove", ["sk", "id_"])
def test_act_invalid_session(key_to_remove, session_data):
    session_data.pop(key_to_remove)
    with raises(ValueError):
        translate.act("", session_data, {})


def test_act_init(
    boto3_mock, boto3_session_mock, session_data, session_id, resource_mock, table_name
):
    resource_mock.Table.return_value.get_item.return_value = {
        "Item": {"languages": ["en, ne, fr, xx"]}
    }
    params = {"action": "init"}
    expected = (
        {
            "id_": "1234567890",
            "local": "en",
            "sk": "1234567890",
            "translate": {"state": "closed"},
        },
        [],
    )
    observed = translate.act(table_name, session_data, params)
    assert observed == expected


def test_build_unexpected_state(mocker, session_data, table_name):
    logger_mock = mocker.patch("lib.translate.logger")
    session_data["translate"]["state"] = "unexpected"
    expected = {
        "body": '<div id="language-picker" class="language no-padding no-margin" '
        'hx-trigger="click" hx-swap="outerHTML swap:100ms" '
        'hx-get="/ui/translate?action=open" hx-params="*"><ul '
        'class="no-padding no-margin"><li class="lang-btn">EN<img '
        'src="./flags/us.svg"></li></ul></div>',
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    observed = translate.build(table_name, session_data)
    assert observed == expected
    logger_mock.warning.assert_called()


def test_build_open(resource_mock, session_data, table_name):
    session_data["translate"]["state"] = "open"
    resource_mock.return_value.Table.return_value.get_item.return_value = {
        "Item": {"languages": ["en", "ne", "fr", "xx"]}
    }
    expected = {
        "body": '<div id="language-picker" class="language no-padding no-margin"><ul '
        'class="no-margin no-padding"><li hx-trigger="click" '
        'hx-swap="outerHTML swap:100ms" hx-get="/ui/translate" '
        'hx-vals="{&quot;action&quot;: &quot;en&quot;}" '
        'hx-target="#language-picker" hx-params="*" class="lang-btn">EN<img '
        'src="./flags/us.svg"></li><li hx-trigger="click" hx-swap="outerHTML '
        'swap:100ms" hx-get="/ui/translate" hx-vals="{&quot;action&quot;: '
        '&quot;fr&quot;}" hx-target="#language-picker" hx-params="*" '
        'class="lang-btn">FR<img src="./flags/fr.svg"></li><li '
        'hx-trigger="click" hx-swap="outerHTML swap:100ms" '
        'hx-get="/ui/translate" hx-vals="{&quot;action&quot;: '
        '&quot;ne&quot;}" hx-target="#language-picker" hx-params="*" '
        'class="lang-btn">NE<img src="./flags/ne.svg"></li><li '
        'hx-trigger="click" hx-swap="outerHTML swap:100ms" '
        'hx-get="/ui/translate" hx-vals="{&quot;action&quot;: '
        '&quot;xx&quot;}" hx-target="#language-picker" hx-params="*" '
        'class="lang-btn">XX<img src="./flags/xx.svg"></li></ul></div>',
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    observed = translate.build(table_name, session_data)
    assert observed == expected


def test_build_closed(session_data, table_name):
    expected = {
        "body": '<div id="language-picker" class="language no-padding no-margin" '
        'hx-trigger="click" hx-swap="outerHTML swap:100ms" '
        'hx-get="/ui/translate?action=open" hx-params="*"><ul '
        'class="no-padding no-margin"><li class="lang-btn">EN<img '
        'src="./flags/us.svg"></li></ul></div>',
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    observed = translate.build(table_name, session_data)
    assert observed == expected
