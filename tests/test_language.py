from lib import language
from pytest import fixture, mark, raises


@fixture
def boto3_mock(mocker):
    return mocker.patch("lib.language.boto3")


@fixture
def boto3_session_mock(mocker):
    return mocker.patch("lib.language.session.boto3")


@fixture
def client_mock(boto3_mock):
    return boto3_mock.client


@fixture
def resource_mock(boto3_mock):
    return boto3_mock.resource


def test_add_supported_language(resource_mock, table_name):
    assert language.add_supported(resource_mock, table_name, "yo")
    resource_mock.Table.return_value.put_item.assert_called()


def test_remove_supported(resource_mock, table_name):
    resource_mock.Table.return_value.get_item.return_value = {
        "Item": {"languages": ["aa", "bb", "yo"]}
    }
    assert language.remove_supported(resource_mock, table_name, "yo")
    resource_mock.Table.return_value.put_item.assert_called()


def test_remove_supported_already_removed(resource_mock, table_name):
    resource_mock.Table.return_value.get_item.return_value = {
        "Item": {"languages": ["aa", "bb", "yo"]}
    }
    assert language.remove_supported(resource_mock, table_name, "lo")
    resource_mock.Table.return_value.put_item.assert_not_called()


def test_add_supported_language_already_supported(resource_mock, table_name):
    resource_mock.Table.return_value.get_item.return_value = {
        "Item": {"languages": ["yo"]}
    }
    assert language.add_supported(resource_mock, table_name, "yo")
    resource_mock.Table.return_value.put_item.assert_not_called()


def test_get_supported_languages(resource_mock, table_name):
    languages = ["en", "fr", "uk"]
    resource_mock.Table.return_value.get_item.return_value = {
        "Item": {"languages": languages}
    }
    assert language.get_supported(resource_mock, table_name) == languages


def test_determine_unsupported_languages(
    mocker, resource_mock, table_name, client_mock
):
    mocker.patch("lib.language.get_supported", return_value=["en"])
    mocker.patch(
        "lib.language.get_processed",
        return_value={"fr": "yolo", "en": "yala"},
    )
    s3_client = client_mock("s3")
    observed = language.determine_unsupported(
        resource_mock, table_name, s3_client, "bucket"
    )
    expected = [("fr", "yolo")]
    assert observed == expected


def test_get_language_keys(client_mock):
    s3_uri = "s3://bucket/key"
    s3_client = client_mock("s3")
    decode_mock = s3_client.get_object.return_value.__getitem__.return_value.read.return_value.decode
    decode_mock.return_value.split.return_value = ["a", "b"]
    observed = language.get_keys(s3_client, s3_uri)
    expected = ["a", "b"]
    assert observed == expected


def test_get_processed_languages(client_mock):
    s3_client = client_mock("s3")
    s3_client.list_objects_v2.return_value = {"Contents": {"Key": ["yolo/fr.en.txt"]}}
    observed = language.get_processed(s3_client, "bucket")
    expected = {"fr": "yolo/fr.en.txt"}
    assert observed == expected


def test_s3_get_object_by_uri_not_s3_uri(client_mock):
    s3_client = client_mock("s3")
    with raises(ValueError):
        language.s3_get_object_by_uri(s3_client, "http://yo/lo.txt")


def test_update_supported_languages(mocker, resource_mock, table_name, client_mock):
    rsrc = resource_mock("dynamodb")
    s3_client = client_mock("s3")
    mocker.patch(
        "lib.language.determine_unsupported",
        return_value=[("fr", "fr.en.txt"), ("yo", "yo.en.txt"), ("lo", "lo.en.txt")],
    )
    mocker.patch("lib.language.get_keys", return_value=["a", "b"])
    s3_client.get_object.return_value.__getitem__.return_value.read.return_value.decode.return_value = "aye\nbee"
    rsrc.put_item.return_value = True
    observed = language.update_supported(
        rsrc, table_name, s3_client, "bucket", "s3://src/keys.txt"
    )
    assert observed


def test_update_supported_len_mismatch(mocker, resource_mock, table_name, client_mock):
    rsrc = resource_mock("dynamodb")
    s3_client = client_mock("s3")
    mocker.patch(
        "lib.language.determine_unsupported",
        return_value=[("fr", "fr.en.txt"), ("yo", "yo.en.txt"), ("lo", "lo.en.txt")],
    )
    mocker.patch("lib.language.get_keys", return_value=["a"])
    s3_client.get_object.return_value.__getitem__.return_value.read.return_value.decode.return_value = "aye\nbee"
    rsrc.put_item.return_value = True
    with raises(ValueError):
        language.update_supported(
            rsrc, table_name, s3_client, "bucket", "s3://src/keys.txt"
        )


def test_handler(mocker, resource_mock, table_name, client_mock):
    env_vars = {
        "ddb_table_name": "table",
        "language_bucket_name": "bucket",
        "source_keys_uri": "uri",
    }
    mocker.patch("lib.language.update_supported", return_value=True)
    mocker.patch("lib.language.os.environ", return_value=env_vars)
    assert language.handler({}, mocker.Mock("Lambda Context"))


@mark.parametrize(
    "env_vars",
    (
        {"ddb_table_name": "table", "language_bucket_name": "bucket"},
        {"ddb_table_name": "table", "source_keys_uri": "uri"},
        {"language_bucket_name": "bucket", "source_keys_uri": "uri"},
    ),
)
def test_handler_missing_env(env_vars, mocker, resource_mock, table_name, client_mock):
    mocker.patch("lib.language.update_supported", return_value=True)
    mocker.patch("lib.language.os.environ", env_vars)
    with raises(ValueError):
        language.handler({}, mocker.Mock("Lambda Context"))
