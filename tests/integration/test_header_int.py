from pytest import fixture
from lib import header
import boto3


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
    assert header.build(table_name, {})
