from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Class
from basilico.elements import Div, Li, Span, Text, Ul
from lib import return_
import boto3
import lens
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


SKILLS_HEADING_SK = "heading#skills"


@xray_recorder.capture("## Applying skills template")
def apply_template(data: list[str], heading: str) -> str:
    template = Div(
        Class("skills"),
        htmx.Get("/ui/skills"),
        htmx.Swap("outerHTML"),
        Span(Class("heading"), Text(heading)),
        Ul(*(Li(Class("bullets"), Text(skill)) for skill in data)),
    )
    return template.string()


@xray_recorder.capture("## Building skills body")
def build(
    table_name: str, session_data: dict[str, str], **_kwargs
) -> return_.Returnable:
    logger.debug("Starting skills build")
    ddb_client = boto3.client("dynamodb")
    localization: str = session_data["local"]
    heading: str = get_heading(ddb_client, localization, table_name)
    data: list[str] = get_data(ddb_client, localization, table_name)
    return return_.http(
        body=apply_template(data=data, heading=heading), status_code=200
    )


@xray_recorder.capture("## Getting skills data")
def get_data(client, localization: str, table_name: str) -> list[str]:
    kce = "pk = :pkval AND begins_with ( sk, :skval )"
    response = client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": localization},
            ":skval": {"S": "skill"},
        },
    )
    return [lens.focus(row, ["text", "S"]) for row in response["Items"]]


def get_heading(client, localization: str, table_name: str) -> str:
    response = client.get_item(
        TableName=table_name,
        Key={"pk": {"S": localization}, "sk": {"S": SKILLS_HEADING_SK}},
    )
    return lens.focus(response, ["Item", "text", "S"])
