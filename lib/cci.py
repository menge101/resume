from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Class
from basilico.elements import Div, Element, Li, Raw, Span, Text, Ul
from lib import return_, session
from typing import Optional
import boto3
import lens
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


CCI_HEADING_SK = "heading#cci"


class Cci:
    def __init__(self):
        self.name = None
        self.title = None
        self.start_month = None
        self.start_year = None
        self.end_month = None
        self.end_year = None
        self.achievements = {}

    def add(self, attr1, value, attr2: Optional[str] = None):
        if attr1 == "achievement":
            if not attr2:
                raise ValueError("Index value must be set for bullet entries")
            self.achievements[attr2] = value
        else:
            attr1 = attr1.replace("-", "_")
            self.__setattr__(attr1, value)

    def dates(self):
        if not self.start_year and not self.end_year:
            return None
        start_string = self.start_year
        if self.start_month:
            start_string = f"{self.start_month} {start_string}"
        end_string = self.end_year
        if self.end_month:
            end_string = f"{self.end_month} {end_string}"
        return f"{start_string} - {end_string}"

    def render(self) -> Element:
        if self.simple():
            return Ul(Class("no-bullets"), Li(Span(Class("name"), Text(self.name))))
        return Ul(
            Class("no-bullets"),
            Li(
                Span(Class("name"), Text(self.name)),
                Raw("&nbsp;&nbsp;&#183;&nbsp;&nbsp;"),
                Span(Class("dates"), Text(self.dates())),
            ),
            Li(Class("cci"), Span(Class("title"), Text(self.title))),
            Li(
                Ul(
                    Class("bullets"),
                    *(
                        Li(Class("bullets"), Text(bullet))
                        for bullet in self.achievements.values()
                    ),
                ),
            ),
        )

    def simple(self):
        return (
            self.name and not self.achievements and not self.dates() and not self.title
        )


@xray_recorder.capture("## CCI act function")
def act(
    _data_table_name: str, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying cci template")
def apply_template(data: list[Element], heading: str) -> str:
    template = Div(
        Class("cci"),
        htmx.Get("/ui/cci"),
        htmx.Swap("outerHTML"),
        htmx.Trigger("language-updated from:body"),
        Span(Class("heading"), Text(heading)),
        *(datum for datum in data),
    )
    try:
        return template.string()
    except AttributeError as ae:
        logger.exception(ae)
        logger.error("Unexpected none value")
        raise ae


@xray_recorder.capture("## Building cci body")
def build(
    table_name: str, session_data: dict[str, str], *_args, **_kwargs
) -> return_.Returnable:
    logger.debug("Starting cci build")
    ddb_client = boto3.client("dynamodb")
    localization: str = session_data.get("local", "en")
    heading: str = get_heading(ddb_client, localization, table_name)
    data: list[Element] = get_data(ddb_client, localization, table_name)
    return return_.http(
        body=apply_template(data=data, heading=heading), status_code=200
    )


@xray_recorder.capture("## Getting cci data")
def get_data(client, localization: str, table_name: str) -> list[Element]:
    kce = "pk = :pkval AND begins_with ( sk, :skval )"
    response = client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": localization},
            ":skval": {"S": "cci"},
        },
    )
    return package_data(response["Items"])


def get_heading(client, localization: str, table_name: str) -> str:
    response = client.get_item(
        TableName=table_name,
        Key={"pk": {"S": localization}, "sk": {"S": CCI_HEADING_SK}},
    )
    return lens.focus(response, ["Item", "text", "S"])


@xray_recorder.capture("## Packaging cci data")
def package_data(rows: list[dict[str, str]]) -> list[Element]:
    records: dict[str, Cci] = {}
    for row in rows:
        keychain = lens.focus(row, ["sk", "S"])
        key_pieces = keychain.split("#")
        value = lens.focus(row, ["text", "S"])
        idx = key_pieces[1]
        key_attr = key_pieces[2]
        try:
            ach_idx = key_pieces[3]
        except IndexError:
            ach_idx = None
        try:
            records[idx]
        except KeyError:
            records[idx] = Cci()
        records[idx].add(key_attr, value, ach_idx)
    return [record.render() for record in records.values()]
