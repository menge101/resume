from pytest import fixture
from lib import header


@fixture
def boto3_mock(client_raw_response, mocker):
    boto3_mock = mocker.patch("lib.header.boto3")
    boto3_mock.client.return_value.batch_get_item.return_value = client_raw_response


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


def test_build(boto3_mock, table_name):
    assert header.build(table_name, {})


def test_unpack_response(client_raw_response, fake_data, table_name):
    value = header.unpack_response(client_raw_response, table_name)
    for key in value.keys():
        assert fake_data[key] == value[key]
