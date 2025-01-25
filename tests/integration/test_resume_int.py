from pytest import fixture
from lib import resume


@fixture
def event_no_cookie():
    return {}


@fixture
def event_with_cookie(session_id):
    return {"cookies": [f"id_={session_id}"]}


@fixture
def yolo():
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/ui/translate",
        "rawQueryString": "action=EN",
        "cookies": ["id_=3641c9ca-dc01-11ef-b569-ddc111ab69cb"],
        "headers": {
            "x-amz-content-sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "content-length": "0",
            "x-amzn-tls-version": "TLSv1.3",
            "cookie": "id_=3641c9ca-dc01-11ef-b569-ddc111ab69cb",
            "x-amz-date": "20250126T232712Z",
            "x-forwarded-proto": "https",
            "x-amz-source-account": "779846793683",
            "x-forwarded-port": "443",
            "x-forwarded-for": "74.111.173.74",
            "x-amz-security-token": "IQoJb3JpZ2luX2VjEEgaCXVzLWVhc3QtMSJGMEQCIDeOl2f5sTMKJIHVqHgFY2Dt7EYwBcbOxMLueRgqH1HbAiBXr0WbYqiPxP7XpGhKJUAZChmznybvVHWsxno5btzwdCqOAghQEAAaDDg1NjM2OTA1MzE4MSIMbcidGIUHe47fRqC/KusB5an4RcFHVtydj+nFw++X98GE3KZO1ImMcT1F/qSvuiJ3lnKgkLG3SRzdoGGPibzSn1XDldV8pBKtUgnWyeBZwLR64asoEGrFLvDUXA7e+aX0aN7SNm8rQYrryW76G+5ujGNqm9DgSjLGkOGZIILzp/AAXYIiSoSe9cWpAxfh4qzzQnHPphx9CK+Re+ISHgfQTPXKCPTNAiZqggPKdxNim7BMgbWZvjs3jNPV4oems2zY9VIKGyORokghczPiHmSY3TUpedJZIdgDAty9SccOCtRA8hNDD9JvelXkJv+vUpkG0E0krAc3eefFuzCVhtu8BjqQAf0gXc+jAQ/RFZ7eV4HO4F92KKmVxzAeTR50k86OjWu7NohxzSOyCxSwauDhyeQUTYZnLVygpBMacDJI1aUyU4daK+NmmH5XfjJUxT2v+WOZiYI1FWqUsW1CiPmBb2hQGIofNR0/wy0dLnm/mD4MtEN+JnKazQd0nb0vZDqz1u3FQAHG5N8srUpouKEpf6bczw==",
            "pragma": "no-cache",
            "via": "2.0 999e0c944d96e4c2945aab8389961e9c.cloudfront.net (CloudFront)",
            "x-amz-source-arn": "arn:aws:cloudfront::779846793683:distribution/E6EV5I0TSP4B3",
            "x-amzn-tls-cipher-suite": "TLS_AES_128_GCM_SHA256",
            "x-amzn-trace-id": "Self=1-6796c4d0-2039a0207b4a79a101b9e6ad;Root=1-6796c4d0-2ffe73725f2f45a40196d788",
            "host": "asrw77kxs44ggma2vcbcwqlpiq0iarbz.lambda-url.us-east-1.on.aws",
            "cache-control": "no-cache",
            "x-amz-cf-id": "lPGBpeYn-bJnaI9ZGKJMu7YaWOHUUM5czadSYUssdvb7ubZnFvk2Ew==",
            "user-agent": "Amazon CloudFront",
        },
        "queryStringParameters": {"action": "EN"},
        "requestContext": {
            "accountId": "856369053181",
            "apiId": "asrw77kxs44ggma2vcbcwqlpiq0iarbz",
            "authorizer": {
                "iam": {
                    "accessKey": "ASIA4OY4SXX6WWG33IVR",
                    "accountId": "856369053181",
                    "callerId": "AROA4OY4SXX6VEIZRJRCJ:OriginAccessSession",
                    "cognitoIdentity": None,
                    "principalOrgId": None,
                    "userArn": "arn:aws:sts::856369053181:assumed-role/OriginAccessControlRole/OriginAccessSession",
                    "userId": "AROA4OY4SXX6VEIZRJRCJ:OriginAccessSession",
                }
            },
            "domainName": "asrw77kxs44ggma2vcbcwqlpiq0iarbz.lambda-url.us-east-1.on.aws",
            "domainPrefix": "asrw77kxs44ggma2vcbcwqlpiq0iarbz",
            "http": {
                "method": "GET",
                "path": "/ui/translate",
                "protocol": "HTTP/1.1",
                "sourceIp": "64.252.68.11",
                "userAgent": "Amazon CloudFront",
            },
            "requestId": "81b3cc83-e75c-401a-9999-04a21ee14127",
            "routeKey": "$default",
            "stage": "$default",
            "time": "26/Jan/2025:23:27:12 +0000",
            "timeEpoch": 1737934032788,
        },
        "isBase64Encoded": False,
    }


@fixture
def session(resource, session_id, table):
    tbl = resource.Table(table)
    tbl.put_item(
        Item={"pk": "session", "sk": session_id, "id_": session_id, "local": "en"}
    )
    return session_id


def test_handle_session_no_session(event_no_cookie, table):
    observed = resume.handle_session(event_no_cookie, table)
    expected = {"local": "en", "id_": None}
    assert observed == expected


def test_handle_session(event_with_cookie, session, table):
    observed = resume.handle_session(event_with_cookie, table)
    expected = {"pk": "session", "sk": session, "local": "en", "id_": session}
    assert observed == expected
