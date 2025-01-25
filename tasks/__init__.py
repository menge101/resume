from invoke import Collection, task, Task
from typing import cast
import boto3
import csv
import os


from .translate import translate_collection


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
