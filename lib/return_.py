def error(exception: Exception, status_code: int) -> dict:
    body = f"<div>\nError: {str(exception)}\n</div>"
    return {
        "body": body,
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {"Content-Type": "text/html"},
    }


def http(body, status_code):
    return {
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": status_code,
        "body": body,
    }
