#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
import pytest

from quilt3distribute import Dataset


@pytest.fixture
def example_csv(data_dir):
    return data_dir / "example.csv"


@pytest.fixture
def example_frame(example_csv):
    return pd.read_csv(example_csv)


@pytest.fixture
def repeated_values_frame(data_dir):
    return pd.read_csv(data_dir / "repeated_values_example.csv")


@pytest.fixture
def same_filenames_frame(data_dir):
    return pd.read_csv(data_dir / "same_filenames_example.csv")


@pytest.fixture
def example_readme(data_dir):
    return data_dir / "README.md"


def test_dataset_init_csv(example_csv, example_readme):
    Dataset(example_csv, "test_dataset", "me", example_readme)


@pytest.mark.parametrize("dataset", [
    pytest.param("/this/does/not/exist.csv", marks=pytest.mark.raises(exception=FileNotFoundError)),
    pytest.param(Path("/this/does/not/exist.csv"), marks=pytest.mark.raises(exception=FileNotFoundError))
])
def test_dataset_init_fail_csv_does_not_exist(example_readme, dataset):
    Dataset(dataset, "test_dataset", "me", example_readme)


def test_dataset_init_fail_csv_is_dir(data_dir, example_readme):
    with pytest.raises(IsADirectoryError):
        Dataset(data_dir, "test_dataset", "me", example_readme)


def test_dataset_init_frame(example_frame, example_readme):
    Dataset(example_frame, "test_dataset", "me", example_readme)


@pytest.mark.parametrize("dataset", [
    (pd.DataFrame([{"hello": "world"}, {"hello": "jackson"}])),
    pytest.param(1, marks=pytest.mark.raises(exception=TypeError)),
    pytest.param(("wrong", "type"), marks=pytest.mark.raises(exception=TypeError))
])
def test_dataset_init_types(example_readme, dataset):
    Dataset(dataset, "test_dataset", "me", example_readme)


@pytest.mark.parametrize("readme_path", [
    pytest.param("/this/does/not/exist.md", marks=pytest.mark.raises(exception=FileNotFoundError)),
    pytest.param(Path("/this/does/not/exist.md"), marks=pytest.mark.raises(exception=FileNotFoundError))
])
def test_dataset_init_fail_readme_does_not_exist(example_frame, readme_path):
    Dataset(example_frame, "test_dataset", "me", readme_path)


def test_dataset_init_fail_readme_is_dir(example_frame, data_dir):
    with pytest.raises(IsADirectoryError):
        Dataset(example_frame, "test_dataset", "me", data_dir)


@pytest.mark.parametrize("name", [
    ("test_dataset"),
    ("test-dataset"),
    ("test dataset"),
    ("Test Dataset"),
    ("TEsT-DaTAseT"),
    ("test_dataset_1234"),
    pytest.param("////This///Will///Fail////", marks=pytest.mark.raises(exception=ValueError)),
    pytest.param("@@@~!(@*!_~*~ADSH*@Hashd87g)", marks=pytest.mark.raises(exception=ValueError))
])
def test_dataset_return_or_raise_approved_name(example_frame, example_readme, name):
    Dataset(example_frame, name, "me", example_readme)


@pytest.fixture
def no_additions_dataset(example_frame, example_readme):
    return Dataset(example_frame, "test_dataset", "me", example_readme)


def test_dataset_props(no_additions_dataset):
    assert no_additions_dataset.data is not None
    newly_generated_readme = no_additions_dataset.readme
    assert no_additions_dataset.readme == newly_generated_readme


@pytest.mark.parametrize("usage_doc_or_link", [
    ("https://docs.quiltdata.com"),
    ("https://docs.quiltdata.com/walkthrough/installing-a-package"),
    ("https://docs.quiltdata.com/walkthrough/reading-from-a-package")
])
def test_dataset_readme_usage_attachment(no_additions_dataset, usage_doc_or_link):
    no_additions_dataset.add_usage_doc(usage_doc_or_link)


@pytest.mark.parametrize("license_doc_or_link", [
    ("https://opensource.org/licenses/MIT"),
    ("https://opensource.org/licenses/BSD-2-Clause"),
    ("https://opensource.org/licenses/MPL-2.0")
])
def test_dataset_readme_license_attachment(no_additions_dataset, license_doc_or_link):
    no_additions_dataset.add_license(license_doc_or_link)


@pytest.mark.parametrize("columns", [
    (["Structure"]),
    (["CellId", "Structure"]),
    pytest.param(["DoesNotExist"], marks=pytest.mark.raises(exception=ValueError)),
    pytest.param(["DoesNotExist1", "DoesNotExist2"], marks=pytest.mark.raises(exception=ValueError))
])
def test_dataset_set_metadata_columns(no_additions_dataset, columns):
    no_additions_dataset.set_metadata_columns(columns)


@pytest.mark.parametrize("columns", [
    (["3dReadPath"]),
    (["3dReadPath", "2dReadPath"]),
    pytest.param(["DoesNotExistPath"], marks=pytest.mark.raises(exception=ValueError)),
    pytest.param(["DoesNotExistPath1", "DoesNotExistPath2"], marks=pytest.mark.raises(exception=ValueError))
])
def test_dataset_set_path_columns(no_additions_dataset, columns):
    no_additions_dataset.set_path_columns(columns)


@pytest.mark.parametrize("columns", [
    ({"3dReadPath": "3dImages"}),
    ({"3dReadPath": "3dImages", "2dReadPath": "2dImages"}),
    pytest.param({"DNE": "DNELabeled"}, marks=pytest.mark.raises(exception=ValueError)),
    pytest.param({"DNE1": "DNELabeled1", "DNE2": "DNELabeled2"}, marks=pytest.mark.raises(exception=ValueError))
])
def test_dataset_set_column_names_map(no_additions_dataset, columns):
    no_additions_dataset.set_column_names_map(columns)


def test_dataset_set_extra_files_exists(no_additions_dataset, example_readme):
    no_additions_dataset.set_extra_files([example_readme])
    no_additions_dataset.set_extra_files({"extra": [example_readme]})


@pytest.mark.parametrize("files", [
    pytest.param(["/this/does/not/exist.png"], marks=pytest.mark.raises(exception=FileNotFoundError)),
    pytest.param({"extras": ["/this/does/not/exist.png"]}, marks=pytest.mark.raises(exception=FileNotFoundError))
])
def test_dataset_set_extra_files_fails(no_additions_dataset, files):
    no_additions_dataset.set_extra_files(files)


@pytest.fixture
def extra_additions_dataset(example_frame, example_readme):
    ds = Dataset(example_frame, "test_dataset", "me", example_readme)
    ds.set_path_columns(["2dReadPath"])
    ds.set_extra_files([example_readme])
    ds.set_column_names_map({"2dReadPath": "MappedPath"})
    ds.set_metadata_columns(["Structure"])
    return ds


@pytest.mark.parametrize("push_uri", [
    (None),
    ("s3://fake-uri")
])
def test_dataset_distribute(no_additions_dataset, extra_additions_dataset, push_uri):
    with mock.patch("quilt3.Package.push") as mocked_package_push:
        mocked_package_push.return_value = "NiceTryGuy"
        no_additions_dataset.distribute(push_uri, "some message")
        extra_additions_dataset.distribute(push_uri, "some message")


def test_dataset_metadata_numpy_type_casting(example_frame, example_readme):
    # Add numpy column to frame
    example_frame["NumpyTypes"] = np.zeros(9)
    ds = Dataset(example_frame, "test_dataset", "me", example_readme)

    # Add column filled with numpy types to index
    ds.set_metadata_columns(["NumpyTypes"])

    # Just run distribute to make sure that numpy types are cast fine
    ds.distribute()


class SomeDummyObject:
    def __init__(self, a: int):
        self.a = a


def test_dataset_metadata_non_json_serializable_type(example_frame, example_readme):
    # Add non json serializable type to dataframe
    example_frame["BadType"] = [SomeDummyObject(i) for i in range(9)]
    ds = Dataset(example_frame, "test_dataset", "me", example_readme)

    # Add column filled with non serializable type to index
    ds.set_metadata_columns(["BadType"])

    # Check non json serializable type check fails
    with pytest.raises(TypeError):
        ds.distribute()


def test_dataset_auto_metadata_grouping_no_additions(no_additions_dataset):
    # Generate package
    pkg = no_additions_dataset.distribute()

    # Check file groupings available
    assert set(pkg.keys()) == {
        "2dReadPath", "3dReadPath", "MetadataReadPath", "README.md", "metadata.csv", "referenced_files"
    }

    # Check that associates was produced for metadata and nothing else
    for f in pkg["2dReadPath"]:
        assert "associates" in pkg["2dReadPath"][f].meta
        assert len(pkg["2dReadPath"][f].meta) == 1


def test_dataset_auto_metadata_grouping_extra_additions(extra_additions_dataset):
    # Generate package
    pkg = extra_additions_dataset.distribute()

    # Check file groupings available
    assert set(pkg.keys()) == {"MappedPath", "README.md", "metadata.csv", "referenced_files", "supporting_files"}

    # Check that every metadata item is a string because no metadata reduction was needed
    for f in pkg["MappedPath"]:
        assert isinstance(pkg["MappedPath"][f].meta["Structure"], str)


def test_dataset_auto_metadata_grouping_repeated_values(repeated_values_frame, example_readme):
    """
    Because the repeated values dataset has three unique files but has nine rows of data, this function
    checks that there are only three files passed to the package object but that each file has a list of the unique
    CellIds but that because all the structures are the same per file, that the structure has been reduced to a single
    value.
    """
    # Create dataset from frame
    ds = Dataset(repeated_values_frame, "test_dataset", "me", example_readme)
    ds.set_metadata_columns(["CellId", "Structure"])

    # Generate package
    pkg = ds.distribute()

    # Check file groupings available
    assert set(pkg.keys()) == {"SourceReadPath", "README.md", "metadata.csv", "referenced_files"}

    # Check that only three tiffs were attached to package
    assert len(pkg["SourceReadPath"]) == 3

    # Check that CellId is a list because of repeated values but that Structure is a string because always unique
    for f in pkg["SourceReadPath"]:
        assert isinstance(pkg["SourceReadPath"][f].meta["CellId"], list)
        assert isinstance(pkg["SourceReadPath"][f].meta["Structure"], str)


def test_dataset_file_grouping_with_matching_names(same_filenames_frame, example_readme):
    # Create dataset from frame
    ds = Dataset(same_filenames_frame, "test_dataset", "me", example_readme)

    # Generate package
    pkg = ds.distribute()

    # Check file groupings available
    assert set(pkg.keys()) == {"SourceReadPath", "README.md", "metadata.csv", "referenced_files"}

    # Check that 18 unique files were attached to package
    assert len(pkg["SourceReadPath"]) == 18
