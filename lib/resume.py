from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from typing import cast
import logging
import os
import sys


from lib import (
    banner,
    cci,
    dispatch,
    early,
    education,
    experience,
    header,
    return_,
    session,
    skills,
    translate,
)


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


@xray_recorder.capture("## Main handler")
def handler(event: dict, context):
    logger.debug(event)
    logger.debug(str(context))
    try:
        table_name = os.environ["ddb_table_name"]
    except KeyError:
        return return_.error(
            ValueError("Missing environment variable 'ddb_table_name'"), 500
        )
    dispatcher = dispatch.Dispatcher(
        data_table_name=table_name,
        elements={
            "/header": cast(dispatch.Dispatchable, header),
            "/experience": cast(dispatch.Dispatchable, experience),
            "/skills": cast(dispatch.Dispatchable, skills),
            "/education": cast(dispatch.Dispatchable, education),
            "/early": cast(dispatch.Dispatchable, early),
            "/cci": cast(dispatch.Dispatchable, cci),
            "/session": cast(dispatch.Dispatchable, session),
            "/translate": cast(dispatch.Dispatchable, translate),
            "/banner": cast(dispatch.Dispatchable, banner),
        },
        prefix="/ui",
    )
    try:
        return dispatcher.dispatch(event)
    except ValueError as ve:
        logger.exception(ve)
        return return_.error(ve, 400)
    except Exception as e:
        logger.exception(e)
        return return_.error(e, 500)
