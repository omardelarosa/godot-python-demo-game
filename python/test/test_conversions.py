from typing import Dict
from .mocks import Dictionary, Vector3, PyBridgeNode, Array
from python.lib.conversions import Conversions


def walk_and_assert(o1, o2):
    if hasattr(o1, "d"):
        # Handle list, dict, vector
        if isinstance(o1, Array):
            assert o1 == o2
            # recurse on each list item
            for a, b in zip(o1.d, o2.d):
                print("a", "b")
                walk_and_assert(a, b)
        elif isinstance(o1, Dictionary):
            assert o1 == o2
            # recurse on each key and value
            for k, v in o1.d.items():
                walk_and_assert(v, o2.d[k])
        elif isinstance(o1, Vector3):
            assert o1 == o2
            # do not recurse
    else:
        # do not recurse
        assert o1 == o2


class Unserializable:
    pass

    def __str__(self) -> str:
        return "Unserializable"


def test_conversions():
    # Test Python -> GDScript serialization
    example_obj = {
        "a": [1, 2, 3],
        "b": 10,
        "c": {"c_a": {"c_a_a": [1, 2, 3]}, "c_b": "xyz"},
        "grid_map": {(1, 2, 3): 1, (4, 5, 6): 2},
        "unserializable": Unserializable(),
    }

    result = Conversions.serialize_py_to_gd(example_obj)

    expected_result = Dictionary(
        {
            "a": Array([1, 2, 3]),
            "b": 10,
            "c": Dictionary(
                {"c_a": Dictionary({"c_a_a": Array([1, 2, 3])}), "c_b": "xyz"}
            ),
            "grid_map": Array(
                [Array([Vector3(1, 2, 3), 1]), Array([Vector3(4, 5, 6), 2])]
            ),
            "unserializable": "Unserializable",
        }
    )

    walk_and_assert(result, expected_result)

    # Test GDScript -> Python serialization

    deserialized_result = Conversions.serialize_gd_to_py(expected_result)

    expected_deserialized_result = dict(example_obj)

    # NOTE: It is not possible to preserve unique, in-memory types during serialization.  This is an acceptible way to handle that.
    expected_deserialized_result["unserializable"] = "Unserializable"

    # NOTE: the grid_map as dictionary adds complication to implement and is not actually possible from the GDScript side.  Therefore this "information loss" is acceptable, imo.
    expected_deserialized_result["grid_map"] = [[(1, 2, 3), 1], [(4, 5, 6), 2]]

    assert expected_deserialized_result == deserialized_result
