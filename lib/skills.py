from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Class
from basilico.elements import Div, Li, Span, Text, Ul
from lib import return_, session, threading, types
from typing import cast
import lens
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


SKILLS_HEADING_SK = "heading#skills"


@xray_recorder.capture("## Skills act function")
def act(
    _connection_thread: threading.ReturningThread,
    session_data: session.SessionData,
    _params: dict[str, str],
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying skills template")
def apply_template(data: list[str], heading: str) -> str:
    template = Div(
        Class("skills fade no-break-print"),
        htmx.Get("/ui/skills"),
        htmx.Swap("outerHTML"),
        htmx.Trigger("language-updated from:body"),
        Span(Class("bigger"), Text(heading)),
        Ul(Class("bullets"), *(Li(Text(skill)) for skill in data)),
    )
    return template.string()


@xray_recorder.capture("## Building skills body")
def build(
    connection_thread: threading.ReturningThread,
    session_data: dict[str, str],
    *_args,
    **_kwargs,
) -> return_.Returnable:
    logger.debug("Starting skills build")
    table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
    localization: str = session_data.get("local", "en")
    heading: str = get_heading(ddb_client, localization, table_name)
    data: list[str] = get_data(ddb_client, localization, table_name)
    return return_.http(body=apply_template(data=data, heading=heading), status_code=200)


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
