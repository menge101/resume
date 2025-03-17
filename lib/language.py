from lens import lens
from lib import resume, threading, types
from typing import Any, cast
import boto3
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


def add_supported(connection_thread: threading.ReturningThread, language_code: str) -> bool:
    languages: list[str] = get_supported(connection_thread)
    language_code = language_code.lower()
    if language_code in languages:
        return True
    languages.append(language_code)
    _, _, tbl = cast(types.ConnectionThreadResultType, connection_thread.join())
    tbl.put_item(Item={"pk": "languages", "sk": "none", "languages": languages})
    return True


def remove_supported(connection_thread: threading.ReturningThread, language_code: str) -> bool:
    languages: list[str] = get_supported(connection_thread)
    language_code = language_code.lower()
    if language_code not in languages:
        return True
    languages = [language for language in languages if language != language_code]
    _, _, tbl = cast(types.ConnectionThreadResultType, connection_thread.join())
    tbl.put_item(Item={"pk": "languages", "sk": "none", "languages": languages})
    return True


def determine_unsupported(
    connecting_thread: threading.ReturningThread, s3_client, bucket_name: str
) -> list[tuple[str, str]]:
    supported = get_supported(connecting_thread)
    processed = get_processed(s3_client, bucket_name)
    return [(lang_key, obj_key) for lang_key, obj_key in processed.items() if lang_key not in supported]


def get_keys(s3_client, s3_uri: str) -> list[str]:
    response = s3_get_object_by_uri(s3_client, s3_uri)
    return response["Body"].read().decode().split("\n")


def get_processed(s3_client, bucket: str) -> dict[str, str]:
    response = s3_client.list_objects_v2(Bucket=bucket)
    keys = lens.focus(response, ["Contents", "Key"])
    language_keys = filter(lambda x: x.endswith("en.txt"), keys)
    languages = {}
    for key in language_keys:
        key_splits = key.split("/")
        name_splits = key_splits[1].split(".")
        languages[name_splits[0].lower()] = key
    return languages


def get_supported(connection_thread: threading.ReturningThread) -> list[str]:
    _, _, tbl = cast(types.ConnectionThreadResultType, connection_thread.join())
    response = tbl.get_item(Key={"pk": "languages", "sk": "none"})
    return lens.focus(response, ["Item", "languages"], default_result=[])


def handler(event, context):
    logger.debug(event)
    logger.debug(str(context))
    try:
        os.environ["ddb_table_name"]
    except KeyError:
        raise ValueError("Missing environment variable 'ddb_table_name'")
    try:
        lang_bucket_name = os.environ["language_bucket_name"]
    except KeyError:
        raise ValueError("Missing environment variable 'language_bucket_name'")
    try:
        src_keys_uri = os.environ["source_keys_uri"]
    except KeyError:
        raise ValueError("Missing environment variable 'source_keys_uri'")
    s3_client = boto3.client("s3")
    connection_thread = resume.get_table_connection()
    return update_supported(
        connection_thread,
        s3_client=s3_client,
        dest_bucket_name=lang_bucket_name,
        src_keys_uri=src_keys_uri,
    )


def s3_get_object_by_uri(s3_client, s3_uri: str) -> dict[str, Any]:
    s3_prefix, body = s3_uri.split("://")
    if s3_prefix != "s3":
        raise ValueError(f"This, {s3_uri}, does not appear to be a valid s3 URI")
    bucket, key = body.split("/", maxsplit=1)
    return s3_client.get_object(Bucket=bucket, Key=key)


def update_supported(
    connecting_thread: threading.ReturningThread,
    s3_client,
    dest_bucket_name: str,
    src_keys_uri: str,
) -> bool:
    to_proc = determine_unsupported(
        connecting_thread,
        s3_client=s3_client,
        bucket_name=dest_bucket_name,
    )
    keys = get_keys(s3_client=s3_client, s3_uri=src_keys_uri)
    results = []
    for lang_code, lang_obj_path in to_proc:
        values = s3_client.get_object(Bucket=dest_bucket_name, Key=lang_obj_path)["Body"].read().decode().split("\n")
        results.append(bool(write_to_ddb(connecting_thread, keys, values, lang_code)))
        results.append(add_supported(connecting_thread, lang_code))
    return all(results)


def write_to_ddb(
    connection_thread: threading.ReturningThread,
    language_keys: list[str],
    language_values: list[str],
    code: str,
) -> bool:
    if len(language_keys) != len(language_values):
        raise ValueError(f"Keys have length {len(language_keys)}, values have length {len(language_values)}, mismatch")
    _, _, tbl = cast(types.ConnectionThreadResultType, connection_thread.join())
    rows = [
        {"pk": code.lower(), "sk": language_keys[idx], "text": language_values[idx]}
        for idx in range(len(language_keys))
    ]
    results = [bool(tbl.put_item(Item=row)) for row in rows]
    return all(results)
