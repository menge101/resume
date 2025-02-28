from boto3.dynamodb.types import TypeDeserializer
from invoke import Collection, task, Task
from typing import cast
import boto3
import csv
import os


from .translate import translate_collection


def deserialize(data):
    serializer = TypeDeserializer()
    if isinstance(data, list):
        return [deserialize(v) for v in data]
    if isinstance(data, dict):
        try:
            return serializer.deserialize(data)
        except TypeError:
            return {k: deserialize(v) for k, v in data.items()}
    else:
        return data


@task
def read_ddb_table(_ctx, table_name, write_path):
    client = boto3.client("dynamodb")
    pagi = client.get_paginator("scan")
    with open(write_path, "w") as csvoutput:
        writer = csv.DictWriter(csvoutput, fieldnames=["pk", "sk", "text", "languages"])
        writer.writeheader()
        for page in pagi.paginate(
            TableName=table_name, PaginationConfig={"PageSize": 100}
        ):
            items = page["Items"]
            for item in items:
                try:
                    writer.writerow(deserialize(item))
                except ValueError:
                    pass
    return True


@task
def load_ddb_table(_ctx, table_name, source_file_path):
    rsrc = boto3.resource("dynamodb")
    tbl = rsrc.Table(table_name)
    with open(source_file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [row for row in reader]
    for row in rows:
        tbl.put_item(Item=row)
    return True


@task
def upload_dir_content_to_bucket(
    _ctx, source_dir, target_bucket, target_prefix, content_type=None
):
    s3 = boto3.client("s3")
    files = os.listdir(source_dir)
    for file in files:
        s3.upload_file(
            f"{source_dir}/{file}",
            target_bucket,
            f"{target_prefix}/{file}",
            ExtraArgs={"ContentType": content_type},
        )
    return True


ns = Collection()
ns.add_collection(translate_collection, "translate")
ns.add_task(cast(Task, load_ddb_table))
ns.add_task(cast(Task, upload_dir_content_to_bucket))
ns.add_task(cast(Task, read_ddb_table))
