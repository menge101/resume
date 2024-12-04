from basilico.attributes import Class
from basilico.elements import Li, Raw, Text, Ul
from boto3.dynamodb.types import TypeDeserializer
import boto3
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


def apply_template(data):
    template = Ul(
        Li(Class("name"), Text(data["name"])),
        Li(
            Class("other"),
            Raw(
                (
                    f"{data['city']}, {data['state']}  &nbsp;&nbsp;&#183;&nbsp;&nbsp;  "
                    f"{data['email']}  &nbsp;&nbsp;&#183;&nbsp;&nbsp;  {data['github']}"
                )
            ),
        ),
    )
    return template.string()


def build(table_name: str, _session_data: dict[str, str]):
    ddb_client = boto3.client("dynamodb")
    request = {
        table_name: {
            "Keys": [
                {"pk": {"S": "name"}, "sk": {"S": "none"}},
                {"pk": {"S": "city"}, "sk": {"S": "none"}},
                {"pk": {"S": "state"}, "sk": {"S": "none"}},
                {"pk": {"S": "email"}, "sk": {"S": "none"}},
                {"pk": {"S": "github"}, "sk": {"S": "none"}},
            ]
        }
    }
    logger.debug(f"Request: {request}")
    response = ddb_client.batch_get_item(RequestItems=request)
    unpacked_data = unpack_response(response, table_name)
    return apply_template(unpacked_data)


def unpack_response(response: dict, table_name: str) -> dict[str, list[str] | str]:
    responses = response["Responses"][table_name]
    deserializer = TypeDeserializer()
    python_data = {
        deserializer.deserialize(row["pk"]): deserializer.deserialize(row["text"])
        for row in responses
    }
    return python_data
