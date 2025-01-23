from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from typing import Optional
import boto3
import logging
import os
import sys


from lib import cci, early, education, experience, header, return_, session, skills
from lib.dispatch import dispatch


patch_all()

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging_level,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


@xray_recorder.capture("## Decoding session ID from cookie")
def cookie_crumble(event: dict) -> str:
    raw_cookies = event.get("cookies", [])
    cookies = {}
    for cookie in raw_cookies:
        key, value = cookie.split("=", 1)
        cookies[key] = value
    return cookies["id_"]


@xray_recorder.capture("## Retrieving session data from ddb table")
def get_session_data(session_id: str, table_name: str) -> dict[str, Optional[str]]:
    rsrc = boto3.resource("dynamodb")
    tbl = rsrc.Table(table_name)
    response = tbl.get_item(
        Key={"pk": "session", "sk": session_id}, ConsistentRead=True
    )
    logger.debug(f"Session data: {response['Item']}")
    return response["Item"]


@xray_recorder.capture("## Handling session data")
def handle_session(event: dict, table_name: str) -> dict[str, Optional[str]]:
    try:
        session_id = cookie_crumble(event)
    except KeyError:
        return {"local": "en", "id_": None}
    return get_session_data(session_id, table_name)


def handler(event: dict, context):
    logger.debug(event)
    logger.debug(str(context))
    try:
        table_name = os.environ["ddb_table_name"]
    except KeyError:
        return return_.error(
            ValueError("Missing environment variable 'ddb_table_name'"), 500
        )
    session_data: dict[str, Optional[str]] = handle_session(event, table_name)
    try:
        response = dispatch(
            event,
            data_table_name=table_name,
            elements={
                "/header": header.build,
                "/experience": experience.build,
                "/skills": skills.build,
                "/education": education.build,
                "/early": early.build,
                "/cci": cci.build,
                "/": header.build,
                "/session": session.build,
            },
            expected_prefix="/ui",
            session_data=session_data,
        )
        logger.debug(response)
        return response
    except ValueError as ve:
        logger.exception(ve)
        return return_.error(ve, 400)
    except Exception as e:
        logger.exception(e)
        return return_.error(e, 500)
