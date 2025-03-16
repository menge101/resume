from aws_xray_sdk.core import xray_recorder
from basilico.attributes import Class
from basilico.elements import Li, Raw, Text, Ul
from boto3.dynamodb.types import TypeDeserializer
from lib import return_, session
import boto3
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


@xray_recorder.capture("## Header act function")
def act(
    _data_table_name: str, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Header apply template")
def apply_template(data):
    template = Ul(
        Class("no-bullets"),
        Li(Class("name biggest"), Text(data["name"])),
        Li(
            Class("other big"),
            Raw(
                (
                    f"{data['city']}, {data['state']}  &nbsp;&nbsp;&#183;&nbsp;&nbsp;  "
                    f"{data['email']}  &nbsp;&nbsp;&#183;&nbsp;&nbsp;  {data['github']}"
                )
            ),
        ),
    )
    return template.string()


@xray_recorder.capture("## Header build function")
def build(table_name: str, *_args, **_kwargs):
    logger.debug("Starting header build")
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
    response = ddb_client.batch_get_item(RequestItems=request)
    logger.debug(f"Raw batch get item: {response}")
    unpacked_data = unpack_response(response, table_name)
    logger.debug(f"Unpacked data: {unpacked_data}")
    return return_.http(
        body=apply_template(unpacked_data),
        status_code=200,
    )


@xray_recorder.capture("## Header unpack response function")
def unpack_response(response: dict, table_name: str) -> dict[str, list[str] | str]:
    responses = response["Responses"][table_name]
    deserializer = TypeDeserializer()
    python_data = {
        deserializer.deserialize(row["pk"]): deserializer.deserialize(row["text"])
        for row in responses
    }
    return python_data
