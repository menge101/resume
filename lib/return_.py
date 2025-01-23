from typing import cast, NewType, Optional


Returnable = NewType("Returnable", dict[str, bool | dict | int | str])


def error(
    exception: Exception, status_code: int, headers: Optional[dict[str, str]] = None
) -> Returnable:
    body = f"<div>\nError: {str(exception)}\n</div>"
    headers = headers or {}
    return http(body, status_code, headers)


def http(
    body: str,
    status_code: int,
    headers: Optional[dict[str, str]] = None,
    cookies: Optional[list[str]] = None,
) -> Returnable:
    headers = headers or {}
    cookies = cookies or []
    headers["Content-Type"] = "text/html"
    return cast(
        Returnable,
        {
            "headers": headers,
            "isBase64Encoded": False,
            "statusCode": status_code,
            "body": body,
            "cookies": cookies,
        },
    )
