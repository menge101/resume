from pytest import fixture
import boto3


from lib import header


@fixture
def client():
    return boto3.client("dynamodb")


@fixture
def header_data(fake_data, resource, table):
    resource.put_item(Item={"pk": "name", "sk": "none", "text": fake_data["name"]})
    resource.put_item(Item={"pk": "city", "sk": "none", "text": fake_data["city"]})
    resource.put_item(Item={"pk": "state", "sk": "none", "text": fake_data["state"]})
    resource.put_item(Item={"pk": "email", "sk": "none", "text": fake_data["email"]})
    resource.put_item(Item={"pk": "github", "sk": "none", "text": fake_data["github"]})


@fixture
def resource(table_name):
    rsrc = boto3.resource("dynamodb")
    return rsrc.Table(table_name)


def test_build(header_data, table_name):
    assert header.build(table_name)
