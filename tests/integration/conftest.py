from pytest import fixture
import boto3


@fixture
def client():
    return boto3.client("dynamodb")


@fixture
def resource():
    return boto3.resource("dynamodb")


@fixture
def table(client, table_name):
    try:
        _create_table(client, table_name)
    except client.exceptions.ResourceInUseException:
        client.delete_table(TableName=table_name)
        waiter = client.get_waiter("table_not_exists")
        waiter.wait(TableName=table_name, WaiterConfig={"Delay": 10, "MaxAttempts": 10})
        _create_table(client, table_name)
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=table_name, WaiterConfig={"Delay": 10, "MaxAttempts": 10})
    yield table_name
    client.delete_table(TableName=table_name)


def _create_table(client, table_name):
    client.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
