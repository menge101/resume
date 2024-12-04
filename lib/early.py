from basilico.attributes import Class
from basilico.elements import Div, Element, Li, Raw, Span, Text, Ul
import boto3
import lens
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


SKILLS_HEADING_SK = "heading#early"


class EarlyCareer:
    def __init__(self):
        self.name = None
        self.title = None
        self.start_month = None
        self.start_year = None
        self.end_month = None
        self.end_year = None

    def add(self, attr, value):
        attr = attr.replace("-", "_")
        self.__setattr__(attr, value)

    def render(self) -> Element:
        return Li(
            Class("early-career"),
            Span(Class("name"), Text(self.name)),
            Raw("&nbsp;&nbsp;&#183;&nbsp;&nbsp;"),
            Span(Class("title"), Text(self.title)),
            Raw("&nbsp;&nbsp;&#183;&nbsp;&nbsp;"),
            Span(
                Class("dates"),
                Text(
                    f"{self.start_month} {self.start_year} - {self.end_month} {self.start_year}"
                ),
            ),
        )


def apply_template(data: list[EarlyCareer], heading: str) -> str:
    template = Div(
        Class("early-career"),
        Span(Class("heading"), Text(heading)),
        Ul(
            *(datum.render() for datum in data),
        ),
    )
    return template.string()


def build(table_name: str, session_data: dict[str, str], **_kwargs) -> str:
    ddb_client = boto3.client("dynamodb")
    localization: str = session_data["local"]
    heading: str = get_heading(ddb_client, localization, table_name)
    data: list[EarlyCareer] = get_data(ddb_client, localization, table_name)
    return apply_template(data=data, heading=heading)


def get_data(client, localization: str, table_name: str) -> list[EarlyCareer]:
    kce = "pk = :pkval AND begins_with ( sk, :skval )"
    response = client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": localization},
            ":skval": {"S": "early"},
        },
    )
    logger.debug(f"Raw response: {response}")
    return package_data(response["Items"])


def get_heading(client, localization: str, table_name: str) -> str:
    response = client.get_item(
        TableName=table_name,
        Key={"pk": {"S": localization}, "sk": {"S": SKILLS_HEADING_SK}},
    )
    return lens.focus(response, ["Item", "text", "S"])


def package_data(items: list[dict[str, str]]) -> list[EarlyCareer]:
    data: dict[str, EarlyCareer] = {}
    for item in items:
        key = lens.focus(item, ["sk", "S"])
        value = lens.focus(item, ["text", "S"])
        prefix, idx, attr = key.split("#")
        try:
            data[idx]
        except KeyError:
            data[idx] = EarlyCareer()
        data[idx].add(attr, value)
    return list(data.values())
