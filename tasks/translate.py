from invoke import Collection, task, Task
from lib import language, translate
from typing import cast
import boto3


@task
def add_supported_language(_ctx, string_table, language_code):
    ddb_rsrc = boto3.resource("dynamodb")
    language.add_supported(ddb_rsrc, string_table, language_code)
    print(f"Added {language_code} to supported languages in {string_table}")


@task
def remove_supported_language(_ctx, string_table, language_code):
    ddb_rsrc = boto3.resource("dynamodb")
    language.remove_supported(ddb_rsrc, string_table, language_code)
    print(f"Removed {language_code} from supported languages in {string_table}")


@task
def start_job(_ctx, source_bucket_uri, dest_bucket_uri, role_arn, target_language_codes):
    client = boto3.client("translate")
    language_codes = target_language_codes.split(",")
    client.start_text_translation_job(
        InputDataConfig={"S3Uri": source_bucket_uri, "ContentType": "text/plain"},
        OutputDataConfig={"S3Uri": dest_bucket_uri},
        TargetLanguageCodes=language_codes,
        DataAccessRoleArn=role_arn,
        SourceLanguageCode="en",
    )


@task
def upload_en_strings_to_bucket(_ctx, string_table, dest_bucket):
    ddb_client = boto3.client("dynamodb")
    strings = translate.get_existing_en_data(ddb_client, string_table)
    s3_client = boto3.client("s3")
    s3_client.put_object(Body="\n".join(strings.values()), Bucket=dest_bucket, Key="input/en.txt")
    s3_client.put_object(Body="\n".join(strings.keys()), Bucket=dest_bucket, Key="keys/en.txt")


translate_collection = Collection("translate")
translate_collection.add_task(cast(Task, upload_en_strings_to_bucket))
translate_collection.add_task(cast(Task, start_job))
translate_collection.add_task(cast(Task, add_supported_language))
translate_collection.add_task(cast(Task, remove_supported_language))
