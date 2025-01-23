from pytest import fixture
from lib import early


@fixture
def client_mock(mocker):
    return mocker.patch("lib.experience.boto3.client")


@fixture
def data_response():
    return {
        "Items": [
            {"sk": {"S": "early#0#name"}, "text": {"S": "Yolords"}},
            {"sk": {"S": "early#0#title"}, "text": {"S": "Lord of yolos"}},
            {"sk": {"S": "early#0#start-month"}, "text": {"S": "February"}},
            {"sk": {"S": "early#0#start-year"}, "text": {"S": "2022"}},
            {"sk": {"S": "early#0#end-year"}, "text": {"S": "2025"}},
            {"sk": {"S": "early#0#end-month"}, "text": {"S": "January"}},
        ]
    }


@fixture
def real_response():
    return {
        "Items": [
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#0#end-month"},
                "text": {"S": "August"},
            },
            {"pk": {"S": "en"}, "sk": {"S": "early#0#end-year"}, "text": {"S": "2012"}},
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#0#name"},
                "text": {"S": "Philips/Respironics – Validation & Verification"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#0#start-month"},
                "text": {"S": "December"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#0#start-year"},
                "text": {"S": "2008"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#0#title"},
                "text": {"S": "Software Assurance Engineer"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#1#end-month"},
                "text": {"S": "December"},
            },
            {"pk": {"S": "en"}, "sk": {"S": "early#1#end-year"}, "text": {"S": "2008"}},
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#1#name"},
                "text": {"S": "Vocollect - Custom Systems"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#1#start-month"},
                "text": {"S": "July"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#1#start-year"},
                "text": {"S": "2008"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#1#title"},
                "text": {"S": "Quality Assurance Engineer"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#2#end-month"},
                "text": {"S": "June"},
            },
            {"pk": {"S": "en"}, "sk": {"S": "early#2#end-year"}, "text": {"S": "2008"}},
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#2#name"},
                "text": {"S": "Management Science Associates"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#2#start-month"},
                "text": {"S": "June"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#2#start-year"},
                "text": {"S": "2006"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#2#title"},
                "text": {"S": "Quality Assurance Analyst II"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#3#end-month"},
                "text": {"S": "June"},
            },
            {"pk": {"S": "en"}, "sk": {"S": "early#3#end-year"}, "text": {"S": "2006"}},
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#3#name"},
                "text": {"S": "Entigo Corporation"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#3#start-month"},
                "text": {"S": "May"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#3#start-year"},
                "text": {"S": "2003"},
            },
            {
                "pk": {"S": "en"},
                "sk": {"S": "early#3#title"},
                "text": {"S": "Quality Assurance Analyst"},
            },
        ],
        "Count": 24,
        "ScannedCount": 24,
        "ResponseMetadata": {
            "RequestId": "EKGGLV2R9TH2ROFPV6QJSE8VK7VV4KQNSO5AEMVJF66Q9ASUAAJG",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "server": "Server",
                "date": "Mon, 20 Jan 2025 19:48:36 GMT",
                "content-type": "application/x-amz-json-1.0",
                "content-length": "1873",
                "connection": "keep-alive",
                "x-amzn-requestid": "EKGGLV2R9TH2ROFPV6QJSE8VK7VV4KQNSO5AEMVJ9ASUAAJG",
                "x-amz-crc32": "744656714",
            },
            "RetryAttempts": 0,
        },
    }


def test_build(client_mock, data_response, session_data, table_name):
    client_mock.return_value.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.return_value.query.return_value = data_response
    observed = early.build(table_name, session_data)
    expected = (
        '<div class="early-career" hx-get="/ui/early" hx-swap="outerHTML"><span class="heading">yolo</span><ul><li cla'
        'ss="early-career"><span class="name">Yolords</span>&nbsp;&nbsp;&#183;&nbsp;&nbsp;<span class="title">'
        'Lord of yolos</span>&nbsp;&nbsp;&#183;&nbsp;&nbsp;<span class="dates">February 2022 - January 2022</span>'
        "</li></ul></div>"
    )
    assert observed["body"] == expected


def test_real(client_mock, real_response, session_data, table_name):
    client_mock.return_value.get_item.return_value = {"Item": {"text": {"S": "yolo"}}}
    client_mock.return_value.query.return_value = real_response
    observed = early.build(table_name, session_data)
    expected = (
        '<div class="early-career" hx-get="/ui/early" hx-swap="outerHTML"><span class="heading">yolo</span><ul><li cl'
        'ass="early-career"><span class="name">Philips/Respironics – Validation &amp; Verification</span>&nbsp;&nbsp;'
        '&#183;&nbsp;&nbsp;<span class="title">Software Assurance Engineer</span>&nbsp;&nbsp;&#183;&nbsp;&nbsp;<span '
        'class="dates">December 2008 - August 2008</span></li><li class="early-career"><span class="name">Vocollect - '
        'Custom Systems</span>&nbsp;&nbsp;&#183;&nbsp;&nbsp;<span class="title">Quality Assurance Engineer</span>&nbsp;'
        '&nbsp;&#183;&nbsp;&nbsp;<span class="dates">July 2008 - December 2008</span></li><li class="early-career">'
        '<span class="name">Management Science Associates</span>&nbsp;&nbsp;&#183;&nbsp;&nbsp;<span class="title">'
        'Quality Assurance Analyst II</span>&nbsp;&nbsp;&#183;&nbsp;&nbsp;<span class="dates">June 2006 - June 2006'
        '</span></li><li class="early-career"><span class="name">Entigo Corporation</span>&nbsp;&nbsp;&#183;&nbsp;'
        '&nbsp;<span class="title">Quality Assurance Analyst</span>&nbsp;&nbsp;&#183;&nbsp;&nbsp;<span class="dates">'
        "May 2003 - June 2003</span></li></ul></div>"
    )
    assert observed["body"] == expected
