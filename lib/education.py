from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Class
from basilico.elements import Div, Element, Li, Span, Text, Ul
from lib import return_, session
from typing import Optional
import boto3
import lens
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


EDUCATION_HEADING_SK = "heading#school"


class Education:
    def __init__(self):
        self.name = None
        self.location = None
        self.achievements = {}

    def add(self, attr1: str, attr2: Optional[str], value: str) -> None:
        if attr1 == "achievement":
            if not attr2:
                raise ValueError("Achievement index must be set")
            self.achievements[int(attr2)] = value
        else:
            self.__setattr__(attr1, value)

    def render(self) -> Element:
        ach_list = [self.achievements[idx] for idx in range(len(self.achievements))]
        template = Ul(
            Class("no-bullets"),
            Li(
                Span(Class("name"), Text(self.name)),
            ),
            Li(
                Ul(
                    Class("achievements no-bullets no-margin no-padding"),
                    *(Li(Text(t)) for t in ach_list),
                )
            ),
        )
        return template


@xray_recorder.capture("## Education act function")
def act(
    _data_table_name: str, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying education template")
def apply_template(heading: str, data: list[Education]) -> str:
    template = Div(
        htmx.Get("/ui/education"),
        htmx.Swap("outerHTML"),
        htmx.Trigger("language-updated from:body"),
        Class("education no-bullets fade"),
        Span(Class("bigger"), Text(heading)),
        *(school.render() for school in data),
    )
    return template.string()


@xray_recorder.capture("## Building education body")
def build(
    table_name: str, session_data: dict[str, str], *_args, **_kwargs
) -> return_.Returnable:
    logger.debug("Starting education build")
    ddb_client = boto3.client("dynamodb")
    localization: str = session_data.get("local", "en")
    heading: str = get_heading(ddb_client, localization, table_name)
    exp_data: list[Education] = get_data(ddb_client, localization, table_name)
    return return_.http(body=apply_template(heading, exp_data), status_code=200)


@xray_recorder.capture("## Getting education data")
def get_data(client, localization: str, table_name: str) -> list[Education]:
    kce = "pk = :pkval AND begins_with ( sk, :skval )"
    response = client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": localization},
            ":skval": {"S": "edu"},
        },
    )
    return package_data(response["Items"])


def get_heading(client, localization: str, table_name: str) -> str:
    response = client.get_item(
        TableName=table_name,
        Key={"pk": {"S": localization}, "sk": {"S": EDUCATION_HEADING_SK}},
    )
    return lens.focus(response, ["Item", "text", "S"])


@xray_recorder.capture("## Packaging education data")
def package_data(data: list[dict[str, str]]) -> list[Education]:
    objects: dict[int, Education] = {}
    for item in data:
        key: str = lens.focus(item, ["sk", "S"])
        text: str = lens.focus(item, ["text", "S"])
        key_chain = key.split("#")
        index = int(key_chain[1])
        try:
            objects[index]
        except KeyError:
            objects[index] = Education()
        try:
            fourth_key: Optional[str] = key_chain[3]
        except (KeyError, IndexError):
            fourth_key = None
        objects[index].add(key_chain[2], fourth_key, text)
    return [objects[inx] for inx in range(len(objects))]
