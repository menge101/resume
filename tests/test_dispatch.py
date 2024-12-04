from pytest import fixture
from lib import dispatch


@fixture
def http_request_event():
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/ui/element",
        "rawQueryString": "",
        "headers": {
            "x-amz-content-sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "content-length": "0",
            "x-amzn-tls-version": "TLSv1.3",
            "x-amz-date": "20250113T085918Z",
            "x-forwarded-proto": "https",
            "x-amz-source-account": "779846793683",
            "x-forwarded-port": "443",
            "x-forwarded-for": "197.254.28.218",
            "x-amz-security-token": "IQoJb3JpZ2luX2VjEAEaCXVzLWVhc3QtMSJHMEUCIHpiDgHIZR48kZH6zLVyh2xKUh7FI",
            "via": "2.0 c2115407817bd859da50cd8a7221b418.cloudfront.net (CloudFront)",
            "x-amz-source-arn": "arn:aws:cloudfront::779846793683:distribution/E6EV5I0TSP4B3",
            "x-amzn-tls-cipher-suite": "TLS_AES_128_GCM_SHA256",
            "x-amzn-trace-id": "Self=1-6784d5e6-6e53f41b50b7bb583bd6e63b;Root=1-6784d5e6-128581cb1a25f58c",
            "host": "bxdsranrgc5bkf5ph5b66dfz5i0okagy.lambda-url.us-east-1.on.aws",
            "accept-encoding": "gzip,deflate",
            "x-amz-cf-id": "uD2VrFaF-Zy611ClLevG0NSdiY634FlQrA8W-9mkoAWw6vHANZ0h0w==",
            "user-agent": "Amazon CloudFront",
        },
        "requestContext": {
            "accountId": "856369053181",
            "apiId": "bxdsranrgc5bkf5ph5b66dfz5i0okagy",
            "authorizer": {
                "iam": {
                    "accessKey": "ASIA4OY4SXX6RBVEYONU",
                    "accountId": "856369053181",
                    "callerId": "AROA4OY4SXX6VEIZRJRCJ:OriginAccessSession",
                    "cognitoIdentity": None,
                    "principalOrgId": None,
                    "userArn": "arn:aws:sts::856369053181:assumed-role/OriginAccessControlRole/OriginAccessSession",
                    "userId": "AROA4OY4SXX6VEIZRJRCJ:OriginAccessSession",
                }
            },
            "domainName": "bxdsranrgc5bkf5ph5b66dfz5i0okagy.lambda-url.us-east-1.on.aws",
            "domainPrefix": "bxdsranrgc5bkf5ph5b66dfz5i0okagy",
            "http": {
                "method": "GET",
                "path": "/ui/element",
                "protocol": "HTTP/1.1",
                "sourceIp": "130.176.36.140",
                "userAgent": "Amazon CloudFront",
            },
            "requestId": "ac6def0d-d269-44a6-8e0b-9cc27caf3c32",
            "routeKey": "$default",
            "stage": "$default",
            "time": "13/Jan/2025:08:59:18 +0000",
            "timeEpoch": 1736758758971,
        },
        "isBase64Encoded": False,
    }


@fixture
def post_event():
    return {
        "requestContext": {
            "http": {"method": "POST", "path": "/ui/element"},
            "requestId": "yolo",
        },
        "rawQueryString": "",
        "version": "2.0",
    }


@fixture
def unsupported_event():
    return {
        "requestContext": {
            "http": {"method": "GET", "path": "/ui/unsupported"},
            "requestId": "yolo",
        },
        "rawQueryString": "",
        "version": "2.0",
    }


@fixture
def mock_element(mocker):
    return mocker.Mock(name="mock_element")


@fixture
def prefix():
    return "/ui"


@fixture
def table_name():
    return "test-data-table"


def test_dispatch(http_request_event, table_name, mock_element, prefix):
    dispatch.dispatch(
        http_request_event,
        data_table_name=table_name,
        elements={"/element": mock_element},
        expected_prefix=prefix,
    )
    assert mock_element.called


def test_dispatch_post(post_event, table_name, mock_element, prefix):
    observed_response = dispatch.dispatch(
        post_event,
        data_table_name=table_name,
        elements={"/element": mock_element},
        expected_prefix=prefix,
    )
    assert observed_response["statusCode"] == 405


def test_dispatch_unsupported_element(
    unsupported_event, table_name, mock_element, prefix
):
    observed_response = dispatch.dispatch(
        unsupported_event,
        data_table_name=table_name,
        elements={"/element": mock_element},
        expected_prefix=prefix,
    )
    assert observed_response["statusCode"] == 404


def test_dispatch_missing_path(table_name, mock_element, prefix):
    event = {
        "requestContext": {"http": {"method": "GET"}, "requestId": "yolo"},
        "rawQueryString": "",
        "version": "2.0",
    }
    observed_response = dispatch.dispatch(
        event,
        data_table_name=table_name,
        elements={"/element": mock_element},
        expected_prefix=prefix,
    )
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_version(table_name, mock_element, prefix):
    event = {
        "requestContext": {
            "http": {"method": "GET", "path": "/ui/element"},
            "requestId": "yolo",
        },
        "rawQueryString": "",
    }
    observed_response = dispatch.dispatch(
        event,
        data_table_name=table_name,
        elements={"/element": mock_element},
        expected_prefix=prefix,
    )
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_method(table_name, mock_element, prefix):
    event = {
        "requestContext": {"http": {"path": "/ui/element"}, "requestId": "yolo"},
        "rawQueryString": "",
    }
    observed_response = dispatch.dispatch(
        event,
        data_table_name=table_name,
        elements={"/element": mock_element},
        expected_prefix=prefix,
    )
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_request_id(table_name, mock_element, prefix):
    event = {
        "requestContext": {
            "http": {"path": "/ui/element", "method": "GET"},
        },
        "rawQueryString": "",
    }
    observed_response = dispatch.dispatch(
        event,
        data_table_name=table_name,
        elements={"/element": mock_element},
        expected_prefix=prefix,
    )
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_query_string(table_name, mock_element, prefix):
    event = {
        "requestContext": {
            "http": {"path": "/ui/element", "method": "GET"},
            "requestId": "yolo",
        },
    }
    observed_response = dispatch.dispatch(
        event,
        data_table_name=table_name,
        elements={"/element": mock_element},
        expected_prefix=prefix,
    )
    assert observed_response["statusCode"] == 400


def test_no_expected_path(http_request_event, table_name, mock_element):
    dispatch.dispatch(
        http_request_event,
        data_table_name=table_name,
        elements={"/ui/element": mock_element},
    )
    assert mock_element.called
