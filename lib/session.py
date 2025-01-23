from lib import cookie, return_
from typing import Optional
from uuid import uuid1
import boto3
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


DEFAULT_SESSION_VALUES = {"local": {"S": "en"}, "pk": {"S": "session"}}


def build(
    table_name: str, session_data: dict[str, Optional[str]]
) -> return_.Returnable:
    logger.debug(f"Session build: {session_data}")
    logger.debug(f"Table name: {table_name}")
    session_id = session_data.get("id_", None)
    if session_id:
        logger.debug("session exists")
        return return_.http("", 204)
    logger.debug("session does not exist")
    session_id = str(uuid1())
    exp = cookie.expiration_time(24 * 60 * 60)
    logger.debug("Writing session to ddb")
    ddb_client = boto3.client("dynamodb")
    item = DEFAULT_SESSION_VALUES.copy()
    item["sk"] = {"S": session_id}
    item["id_"] = {"S": session_id}
    item["ttl"] = {"N": str(cookie.expiration_as_ttl(exp))}
    ddb_client.put_item(
        TableName=table_name,
        Item=item,
    )
    logger.debug("Session written to ddb")
    session_cookie = cookie.Cookie(
        "id_", session_id, secure=True, http_only=True, expires=exp
    )
    logger.debug(f"Session cookie set: {session_cookie}")
    return return_.http("", 200, cookies=[str(session_cookie)])
