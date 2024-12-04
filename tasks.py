from invoke import task
import boto3
import csv


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
