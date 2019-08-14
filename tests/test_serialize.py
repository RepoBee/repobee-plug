import pytest
import collections

from repobee_plug import containers
from repobee_plug import serialize


@pytest.fixture
def hook_result_mapping():
    hook_results = collections.defaultdict(list)
    for repo_name, hook_name, status, msg, data in [
        (
            "slarse-task-1",
            "junit4",
            containers.Status.SUCCESS,
            "All tests passed",
            {"extra": "data", "arbitrary": {"nesting": "here"}},
        ),
        ("slarse-task-1", "javac", containers.Status.ERROR, "Some stuff failed", None),
        (
            "glassey-task-2",
            "pylint",
            containers.Status.WARNING,
            "-10/10 code quality",
            None,
        ),
    ]:
        hook_results[repo_name].append(
            containers.HookResult(hook=hook_name, status=status, msg=msg, data=data)
        )
    return {repo_name: sorted(results) for reponame, results in hook_results.items()}


def test_serialize_empty_mapping():
    assert serialize.result_mapping_to_json({}) == "{}"


def test_desezialize_empty_json():
    assert serialize.json_to_result_mapping("{}") == {}


def test_lossless_serialization(hook_result_mapping):
    """Test that serializing and then deserializing results in all data being
    recovered.
    """
    expected = dict(hook_result_mapping)

    serialized = serialize.result_mapping_to_json(hook_result_mapping)
    deserialized = serialize.json_to_result_mapping(serialized)
    actual = {repo_name: sorted(results) for repo_name, results in deserialized.items()}

    assert actual == expected
