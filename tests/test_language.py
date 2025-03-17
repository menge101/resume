from lib import language
from pytest import fixture, mark, raises


@fixture
def boto3_mock(mocker):
    return mocker.patch("lib.language.boto3")


@fixture
def boto3_session_mock(mocker):
    return mocker.patch("lib.language.session.boto3")


@fixture
def s3_client_mock(boto3_mock):
    return boto3_mock.client("s3")


def test_add_supported_language(connection_thread_mock, resource_mock, s3_client_mock, table_name):
    resource_mock.get_item.return_value = {"Item": {"languages": ["aa", "bb", "yo"]}}
    assert language.add_supported(connection_thread_mock, "lo")
    resource_mock.put_item.assert_called()


def test_remove_supported(connection_thread_mock, resource_mock, s3_client_mock, table_name):
    resource_mock.get_item.return_value = {"Item": {"languages": ["aa", "bb", "yo"]}}
    assert language.remove_supported(connection_thread_mock, "yo")
    resource_mock.put_item.assert_called()


def test_remove_supported_already_removed(connection_thread_mock, resource_mock, s3_client_mock, table_name):
    resource_mock.get_item.return_value = {"Item": {"languages": ["aa", "bb", "yo"]}}
    assert language.remove_supported(connection_thread_mock, "lo")
    resource_mock.put_item.assert_not_called()


def test_add_supported_language_already_supported(connection_thread_mock, resource_mock):
    resource_mock.get_item.return_value = {"Item": {"languages": ["yo"]}}
    assert language.add_supported(connection_thread_mock, "yo")
    resource_mock.put_item.assert_not_called()


def test_get_supported_languages(connection_thread_mock, resource_mock, table_name):
    languages = ["en", "fr", "uk"]
    resource_mock.get_item.return_value = {"Item": {"languages": languages}}
    assert language.get_supported(connection_thread_mock) == languages


def test_determine_unsupported_languages(connection_thread_mock, mocker, resource_mock, s3_client_mock):
    mocker.patch("lib.language.get_supported", return_value=["en"])
    mocker.patch(
        "lib.language.get_processed",
        return_value={"fr": "yolo", "en": "yala"},
    )
    observed = language.determine_unsupported(connection_thread_mock, s3_client_mock, "bucket")
    expected = [("fr", "yolo")]
    assert observed == expected


def test_get_language_keys(s3_client_mock):
    s3_uri = "s3://bucket/key"
    decode_mock = s3_client_mock.get_object.return_value.__getitem__.return_value.read.return_value.decode
    decode_mock.return_value.split.return_value = ["a", "b"]
    observed = language.get_keys(s3_client_mock, s3_uri)
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


def test_update_supported_languages(connection_thread_mock, mocker, resource_mock, table_name, s3_client_mock):
    mocker.patch(
        "lib.language.determine_unsupported",
        return_value=[("fr", "fr.en.txt"), ("yo", "yo.en.txt"), ("lo", "lo.en.txt")],
    )
    mocker.patch("lib.language.get_keys", return_value=["a", "b"])
    resource_mock.get_item.return_value = {"Item": {"languages": ["aa", "bb", "yo"]}}
    s3_client_mock.get_object.return_value.__getitem__.return_value.read.return_value.decode.return_value = "aye\nbee"
    resource_mock.put_item.return_value = True
    observed = language.update_supported(connection_thread_mock, s3_client_mock, "bucket", "s3://src/keys.txt")
    assert observed


def test_update_supported_len_mismatch(connection_thread_mock, mocker, resource_mock, table_name, s3_client_mock):
    mocker.patch(
        "lib.language.determine_unsupported",
        return_value=[("fr", "fr.en.txt"), ("yo", "yo.en.txt"), ("lo", "lo.en.txt")],
    )
    mocker.patch("lib.language.get_keys", return_value=["a"])
    s3_client_mock.get_object.return_value.__getitem__.return_value.read.return_value.decode.return_value = "aye\nbee"
    resource_mock.put_item.return_value = True
    with raises(ValueError):
        language.update_supported(connection_thread_mock, s3_client_mock, "bucket", "s3://src/keys.txt")


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
