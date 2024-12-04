from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import logging
import os
import sys


from lib import cci, early, education, experience, header, return_, skills
from lib.dispatch import dispatch

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging_level,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)

patch_all()


def get_session_data():
    return {"local": "en"}


@xray_recorder.capture("resume-handler")
def handler(event, context):
    logger.debug(event)
    logger.debug(str(context))
    table_name = os.getenv("ddb_table_name")
    session_data = get_session_data()
    if not table_name:
        raise ValueError("Missing environment variable 'ddb_table_name'")
    try:
        return dispatch(
            event,
            data_table_name=table_name,
            elements={
                "/header": header.build,
                "/htmx": build,
                "/experience": experience.build,
                "/skills": skills.build,
                "/education": education.build,
                "/early": early.build,
                "/cci": cci.build,
            },
            expected_prefix="/ui",
            session_data=session_data,
        )
    except ValueError as ve:
        logger.exception(ve)
        return return_.error(ve, 400)
    except Exception as e:
        logger.exception(e)
        return return_.error(e, 500)


def build(_thing):
    return "<h1>htmx running</h1>"
