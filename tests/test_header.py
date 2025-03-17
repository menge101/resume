from pytest import fixture
from lib import header


@fixture
def client_mock(client_raw_response, mocker):
    client = mocker.MagicMock()
    client.batch_get_item.return_value = client_raw_response
    return client


@fixture
def client_raw_response(fake_data):
    return {
        "Responses": {
            "test_table": [
                {"pk": {"S": "name"}, "text": {"S": fake_data["name"]}},
                {"pk": {"S": "city"}, "text": {"S": fake_data["city"]}},
                {"pk": {"S": "state"}, "text": {"S": fake_data["state"]}},
                {"pk": {"S": "email"}, "text": {"S": fake_data["email"]}},
                {"pk": {"S": "github"}, "text": {"S": fake_data["github"]}},
            ]
        }
    }


def test_apply_template(fake_data):
    assert header.apply_template(fake_data)


def test_build(table_name, connection_thread_mock):
    assert header.build(connection_thread_mock, {})


def test_unpack_response(client_raw_response, fake_data, table_name):
    value = header.unpack_response(client_raw_response, table_name)
    for key in value.keys():
        assert fake_data[key] == value[key]


def test_act():
    data, events = header.act("yolo", {}, {})
    assert data == {}
