from pytest import fixture
from lib import translate


@fixture
def table_real_name():
    return "development-webapp-webapplicationconstructdata33DBB228-10IEC4B2866XC"


@fixture
def translation_destination_bucket_name():
    return "development-translation-translationdestination3f8d-dxomc4g48zcq"


@fixture
def translation_keys_s3_uri():
    return "s3://development-translation-translationsource303b34d4-rwgn7buxzupq/keys/en.txt"


def test_add_supported_language(resource, table):
    added_language = "fr"
    assert translate.add_supported_language(resource, table, added_language)
    assert added_language in translate.get_supported_languages(resource, table)


def test_get_existing_en_data(client, table_real_name):
    assert translate.get_existing_en_data(client, table_real_name)


def test_get_supported_languages(resource, table):
    assert translate.get_supported_languages(resource, table) == []


def test_get_processed_languages(client_s3, translation_destination_bucket_name):
    assert translate.get_processed_languages(client_s3, translation_destination_bucket_name)


def test_s3_get_object_by_uri(client_s3, translation_keys_s3_uri):
    assert translate.s3_get_object_by_uri(client_s3, translation_keys_s3_uri)


def test_update_supported_languages(
    resource,
    table_real_name,
    client_s3,
    translation_destination_bucket_name,
    translation_keys_s3_uri,
):
    assert translate.update_supported_languages(
        resource,
        table_real_name,
        client_s3,
        translation_destination_bucket_name,
        translation_keys_s3_uri,
    )
