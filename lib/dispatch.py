from aws_xray_sdk.core import xray_recorder
from typing import Callable, Optional
import lens
import logging
import os


from lib import return_


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


@xray_recorder.capture("dispatch")
def dispatch(
    event: dict[str, str],
    *,
    data_table_name: str,
    elements: dict[str, Callable],
    expected_prefix: Optional[str] = None,
    session_data: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    try:
        dispatch_info = DispatchInfo(event, expected_prefix)
    except ValueError as ve:
        return return_.error(ve, 400)

    if dispatch_info.method != "GET":
        return return_.error(
            ValueError(f"Method {dispatch_info.method} is not supported"), 405
        )
    try:
        return elements[dispatch_info.path](data_table_name, session_data)
    except KeyError as ke:
        logger.exception(ke)
        logger.error("Invalid element requested")
        return return_.error(ValueError("Not found"), 404)


class DispatchInfo:
    def __init__(self, event: dict, expected_path_prefix: Optional[str] = None):
        self.event = event
        self.method: str = lens.focus(
            event, ["requestContext", "http", "method"], default_result=False
        )
        try:
            self.path: str = self.remove_prefix(
                expected_path_prefix,
                lens.focus(event, ["requestContext", "http", "path"]),
            )
        except lens.FocusingError:
            self.path = None  # type: ignore
        self.request_id: str = lens.focus(
            event, ["requestContext", "requestId"], default_result=False
        )
        self.query_string = lens.focus(event, ["rawQueryString"], default_result=False)
        self.validate()

    @staticmethod
    def remove_prefix(expected_path_prefix: Optional[str], path: str) -> str:
        if expected_path_prefix:
            return path.replace(expected_path_prefix, "")
        return path

    def validate(self) -> None:
        errors = []
        if self.event.get("version") != "2.0":
            errors.append(
                f"Invalid version: {self.event.get("version")}, should be 2.0"
            )
        if self.method is False:
            errors.append("Method field not found")
        if self.path is None:
            errors.append("Path field not found")
        if self.request_id is False:
            errors.append("RequestId field not found")
        if self.query_string is False:
            errors.append("QueryStringParameters field not found")
        if errors:
            raise ValueError(", ".join(errors))
        return
