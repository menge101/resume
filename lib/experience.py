import basilico.elements
from basilico.attributes import Class
from basilico.elements import Div, Li, Raw, Span, Text, Ul
from typing import Optional
import boto3
import lens
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


EXPERIENCE_HEADING_SK = "heading#exp"


class Experience:
    def __init__(self):
        self.name = None
        self.title = None
        self.location = None
        self.start_month = None
        self.start_year = None
        self.end_month = None
        self.end_year = None
        self.bullets = {}

    def add(self, attr1: str, attr2: Optional[str], value: str) -> None:
        if attr1 == "bullet":
            if not attr2:
                raise ValueError("Bullet index must be set for bullets")
            self.bullets[int(attr2)] = value
        elif attr1 and not attr2:
            self.__setattr__(attr1, value)
        elif attr1 == "start" or attr1 == "end":
            real_attr = f"{attr1}_{attr2}"
            self.__setattr__(real_attr, value)

    def end(self):
        if self.end_month and self.end_year:
            return f"{self.end_month} {self.end_year}"
        else:
            return "Present"

    def render(self) -> basilico.elements.Element:
        bullet_list = [self.bullets[idx] for idx in range(len(self.bullets))]
        template = Div(
            Class("job"),
            Ul(
                Li(
                    Span(Class("name"), Text(self.name)),
                    Span(
                        Class("dates"),
                        Raw(
                            f"&nbsp;&nbsp;&#183;&nbsp;&nbsp;{self.start_month} {self.start_year} - {self.end()}"
                        ),
                    ),
                ),
                Li(
                    Class("title-and-loc"),
                    Raw(f"{self.title}&nbsp;&nbsp;&#183;&nbsp;&nbsp;{self.location}"),
                ),
                Li(
                    Ul(
                        Class("bullets"),
                        *(Li(Text(t)) for t in bullet_list),
                    )
                ),
            ),
        )
        return template


def apply_template(heading: str, data: list[Experience]) -> str:
    template = Div(
        Class("experience"),
        Span(Class("heading"), Text(heading)),
        *(job.render() for job in data),
    )
    return template.string()


def build(table_name: str, session_data: dict[str, str], **_kwargs) -> str:
    ddb_client = boto3.client("dynamodb")
    localization: str = session_data["local"]
    heading: str = get_heading(ddb_client, localization, table_name)
    exp_data: list[Experience] = get_data(ddb_client, localization, table_name)
    return apply_template(heading, exp_data)


def get_data(client, localization: str, table_name: str) -> list[Experience]:
    kce = "pk = :pkval AND begins_with ( sk, :skval )"
    response = client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": localization},
            ":skval": {"S": "exp"},
        },
    )
    return package_data(response["Items"])


def get_heading(client, localization: str, table_name: str) -> str:
    response = client.get_item(
        TableName=table_name,
        Key={"pk": {"S": localization}, "sk": {"S": EXPERIENCE_HEADING_SK}},
    )
    return lens.focus(response, ["Item", "text", "S"])


def package_data(data: list[dict[str, str]]) -> list[Experience]:
    objects: dict[int, Experience] = {}
    for item in data:
        key: str = lens.focus(item, ["sk", "S"])
        text: str = lens.focus(item, ["text", "S"])
        key_chain = key.split("#")
        index = int(key_chain[1])
        try:
            objects[index]
        except KeyError:
            objects[index] = Experience()
        try:
            fourth_key: Optional[str] = key_chain[3]
        except (KeyError, IndexError):
            fourth_key = None
        objects[index].add(key_chain[2], fourth_key, text)
    return [objects[inx] for inx in range(len(objects))]
