#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

import os
from tempfile import NamedTemporaryFile, TemporaryDirectory
from types import GeneratorType

import pytest

from zenml.constants import REMOTE_FS_PREFIX
from zenml.logger import get_logger
from zenml.utils import path_utils

logger = get_logger(__name__)

# TODO: [MEDIUM] replace this pattern with Hypothesis pattern
BAD_REMOTE_PREFIXES = ["http://", "12345", "----"]
SAMPLE_FILE_NAMES = ["12345", "important_file.txt", "main.py"]
TEMPORARY_FILE_NAME = "a_file.txt"
TEMPORARY_FILE_SEARCH_PREFIX = "a_f*.*"


def test_walk_function_returns_a_generator_object(tmp_path):
    """Check walk function returns a generator object"""
    assert isinstance(path_utils.walk(str(tmp_path)), GeneratorType)


def test_is_root_when_true():
    """Check is_root returns true if path is the root"""
    assert path_utils.is_root("/")


def test_is_root_when_false(tmp_path):
    """Check is_root returns false if path isn't the root"""
    assert path_utils.is_root(tmp_path) is False


def test_is_dir_when_true(tmp_path):
    """is_dir returns true when path refers to a directory"""
    assert path_utils.is_dir(str(tmp_path))


def test_is_dir_when_false(tmp_path):
    """is_dir returns false when path doesn't refer to a directory"""
    assert (
        path_utils.is_dir(os.path.join(str(tmp_path) + TEMPORARY_FILE_NAME))
        is False
    )


def test_find_files_returns_generator_object_when_file_present(tmp_path):
    """find_files returns a generator object when it finds a file"""
    temp_file = os.path.join(tmp_path, TEMPORARY_FILE_NAME)
    with open(temp_file, "w"):
        assert isinstance(
            path_utils.find_files(tmp_path, TEMPORARY_FILE_SEARCH_PREFIX),
            GeneratorType,
        )


def test_find_files_when_file_present(tmp_path):
    """find_files locates a file within a temporary directory"""
    # TODO: [HIGH] actually test something here
    temp_file = os.path.join(tmp_path, TEMPORARY_FILE_NAME)
    with open(temp_file, "w"):
        assert path_utils.find_files(tmp_path, TEMPORARY_FILE_SEARCH_PREFIX)


def test_find_files_when_file_absent(tmp_path):
    """find_files returns None when it doesn't find a file"""
    # TODO: [HIGH] actually test something here
    temp_file = os.path.join(tmp_path, TEMPORARY_FILE_NAME)
    with open(temp_file, "w"):
        assert path_utils.find_files(tmp_path, "abc*.*")


@pytest.mark.parametrize("filesystem", REMOTE_FS_PREFIX)
def test_is_remote_when_using_remote_prefix(filesystem):
    """is_remote returns True when path starts with one of the TFX remote file prefixes"""
    some_random_path = os.path.join(filesystem + "some_directory")
    assert path_utils.is_remote(some_random_path)


@pytest.mark.parametrize("filesystem", BAD_REMOTE_PREFIXES)
def test_is_remote_when_using_non_remote_prefix(filesystem):
    """is_remote returns False when path doesn't start with a remote prefix"""
    some_random_path = os.path.join(filesystem + "some_directory")
    assert path_utils.is_remote(some_random_path) is False


@pytest.mark.parametrize("sample_file", SAMPLE_FILE_NAMES)
def test_gcs_path_when_true(sample_file):
    """is_gcs checks if a file begins with the prefix `gs`"""
    gs_prefix = "gs://"
    sample_file_path = gs_prefix + sample_file
    assert path_utils.is_gcs_path(sample_file_path)


@pytest.mark.parametrize("filesystem", BAD_REMOTE_PREFIXES)
def test_gcs_path_when_false(filesystem):
    """is_gcs checks that false is returned when file has no `gs` prefix"""
    sample_file_path = filesystem + "test_file.txt"
    assert path_utils.is_gcs_path(sample_file_path) is False


def test_list_dir_returns_a_list_of_file_names():
    """list_dir should return a list of file names inside the queried directory"""
    # TODO: [LOW] replace TemporaryDirectory with pytest's tmp_path
    with TemporaryDirectory() as temp_dir:
        # TODO: [HIGH] replace with the tempfile paradigm
        with NamedTemporaryFile(dir=temp_dir) as temp_file:
            assert path_utils.list_dir(temp_dir) == [temp_file.name]


def test_list_dir_returns_a_list_of_file_paths():
    """list_dir should return a list of file paths inside the queried directory"""
    # TODO: [LOW] replace TemporaryDirectory with pytest's tmp_path
    with TemporaryDirectory() as temp_dir:
        # TODO: [HIGH] replace with the tempfile paradigm
        with NamedTemporaryFile(dir=temp_dir) as temp_file:
            assert path_utils.list_dir(temp_dir) == [
                os.path.join(temp_dir, temp_file.name)
            ]


def test_list_dir_returns_one_result_for_one_file():
    """list_dir should return only one result, when there is only one file created"""
    # TODO: [LOW] replace TemporaryDirectory with pytest's tmp_path
    with TemporaryDirectory() as temp_dir:
        # TODO: [HIGH] replace with the tempfile paradigm
        with NamedTemporaryFile(dir=temp_dir) as _:
            assert len(path_utils.list_dir(temp_dir)) == 1


@pytest.mark.parametrize("sample_file", SAMPLE_FILE_NAMES)
def test_list_dir_returns_empty_list_when_dir_doesnt_exist(sample_file):
    """list_dir should return an empty list when the directory"""
    """doesn't exist"""
    # TODO: [LOW] replace TemporaryDirectory with pytest's tmp_path
    with TemporaryDirectory() as temp_dir:
        not_a_real_dir = os.path.join(temp_dir, sample_file)
        assert isinstance(path_utils.list_dir(not_a_real_dir), list)


@pytest.mark.xfail()
def test_logging_takes_place_on_fail_of_list_dir(caplog):
    """logger should output a debug statement on failure to find directory"""
    not_a_real_dir = "./not_a_dir"
    caplog.set_level(logger.DEBUG)
    path_utils.list_dir(not_a_real_dir)
    assert f"Dir {not_a_real_dir} not found." in caplog.text
