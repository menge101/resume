from invoke import Context
from pytest import fixture
import os
import tasks


@fixture
def context():
    return Context()


@fixture
def data_path(project_root):
    return os.path.join(project_root, "data/resume_data.csv")


@fixture
def table_name():
    return "development-webapp-webapplicationconstructdata33DBB228-10IEC4B2866XC"


def test_ddb_load(context, data_path, table_name):
    assert tasks.load_ddb_table(context, table_name, data_path)


def test_ddb_read(context, table_name):
    assert tasks.read_ddb_table(context, table_name, "testing.csv")
