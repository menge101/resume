from pytest import fixture
import boto3
import csv
import os


from lib import experience


@fixture
def client():
    return boto3.client("dynamodb")


@fixture
def exp_data(en_local, table):
    tbl = boto3.resource("dynamodb").Table(table)
    tbl.put_item(Item={"pk": en_local, "sk": "exp#0", "text": "yo"})
    tbl.put_item(Item={"pk": en_local, "sk": "exp#2", "text": "go"})
    tbl.put_item(Item={"pk": en_local, "sk": "exp#1", "text": "lo"})
    return table


@fixture
def full_data(project_root, table):
    source_file_path = os.path.join(project_root, "data/resume_data.csv")
    rsrc = boto3.resource("dynamodb")
    tbl = rsrc.Table(table)
    with open(source_file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [row for row in reader]
    for row in rows:
        tbl.put_item(Item=row)
    return table


@fixture
def heading_data(en_local, table):
    tbl = boto3.resource("dynamodb").Table(table)
    tbl.put_item(
        Item={
            "pk": en_local,
            "sk": experience.EXPERIENCE_HEADING_SK,
            "text": "Relevant Experience",
        }
    )
    return table


@fixture
def en_local():
    return "en"


def test_get_data(client, en_local, exp_data):
    observed = experience.get_data(client, en_local, exp_data)
    expected = ["yo", "lo", "go"]
    assert observed == expected


def test_get_heading(client, en_local, heading_data):
    observed = experience.get_heading(client, en_local, heading_data)
    expected = "Relevant Experience"
    assert observed == expected


def test_build(en_local, full_data):
    observed = experience.build(en_local, full_data)
    expected = (
        '<div class="experience"><span class="heading">Relevant Experience</span><div '
        'class="job"><ul><li><span class="name">UPMC Enterprises</span><span '
        'class="dates">&nbsp;&nbsp;&#183;&nbsp;&nbsp;February 2022 - January '
        "2025</span></li><li><span "
        'class="title-and-loc">None&nbsp;&nbsp;&#183;&nbsp;&nbsp;None</span></li><li><ul '
        'class="bullets"><li>Implemented an event driven security remediation system '
        "that allowed for nearly-instantaneous response to security "
        "events</li><li>Implemented a log forwarding and aggregation system allowing "
        "for simple cross-organization regulatory compliance</li><li>Implemented a "
        "StackSet deployment and auditing system to enable simple and consistent "
        "management of over 100 AWS accounts</li><li>Designed our team&#x27;s "
        "approach to using AWS CDK with Python, including best practices and "
        "standards for development and security</li><li>Contributed to peer skill "
        'development</li></ul></li></ul></div><div class="job"><ul><li><span '
        'class="name">UPMC Enterprises</span><span '
        'class="dates">&nbsp;&nbsp;&#183;&nbsp;&nbsp;April 2021 - February '
        "2022</span></li><li><span "
        'class="title-and-loc">None&nbsp;&nbsp;&#183;&nbsp;&nbsp;None</span></li><li><ul '
        'class="bullets"><li>Researched Serverless technology and related processes '
        "to inform standards at both the team and company level</li><li>Developed a "
        "system to analyze product&#x27;s Google Analytics data and dynamically "
        "create a load testing profile</li><li>Developed a system to enable control "
        "of Cloud Resources in our performance testing cluster from our "
        "chat-service</li></ul></li></ul></div></div>"
    )
    assert observed == expected
