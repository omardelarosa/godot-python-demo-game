from math import floor
import numpy as np
import os

if os.getenv("PY_ENV") == "test":
    from python.test.mocks import Vector3, Array, Dictionary
else:
    from godot import Vector3, Array, Dictionary


class Conversions:
    @staticmethod
    def vec3_to_tuple(vec3):
        return (int(vec3.x), int(vec3.y), int(vec3.z))

    @staticmethod
    def tup_to_vec3(tup):
        x, y, z = tup
        return Vector3(int(x), int(y), int(z))

    @staticmethod
    def np_to_vec3(np_vec3):
        x, y, z = np_vec3
        return Vector3(x, y, z)

    @staticmethod
    def vec3_to_np(vec):
        return np.array([int(vec.x), int(vec.y), int(vec.z)])

    @staticmethod
    def grid_map_to_vec_list(grid):
        return Array([Array([Vector3(k[0], k[1], k[2]), v]) for k, v in grid.items()])

    @staticmethod
    def serialize_py_to_gd(obj):
        """Convert a python object of list, tuple, dictionary, string, number to GDScript"""

        result = None
        if isinstance(obj, int) or isinstance(obj, float) or isinstance(obj, str):
            result = obj
        elif isinstance(obj, dict):
            tmp_keys = []
            tmp_values = []
            leave_as_list = False
            for k, v in obj.items():
                if isinstance(k, str):
                    tmp_keys.append(k)
                    tmp_values.append(Conversions.serialize_py_to_gd(v))
                # Handle grids or Dict[tuple, int] types
                elif isinstance(k, tuple):
                    tmp_keys.append(Conversions.tup_to_vec3(k))
                    tmp_values.append(Conversions.serialize_py_to_gd(v))
                    leave_as_list = True
                else:
                    print(f"warning: unserializable key {k} encountered")
            if leave_as_list:
                # This handles grid maps, similar to the grid_map_to_vec_list conversion
                result = Array([Array([k, v]) for k, v in zip(tmp_keys, tmp_values)])
            else:
                result = Dictionary(dict(zip(tmp_keys, tmp_values)))
        elif isinstance(obj, list):
            tmp = [Conversions.serialize_py_to_gd(el) for el in obj]
            result = Array(tmp)
        elif isinstance(obj, tuple):
            if len(obj) == 3:
                # Assumes all 3-length tuples are vectors
                result = Conversions.tup_to_vec3(obj)
            else:
                # All others are treated as arrays
                result = Array([Conversions.serialize_py_to_gd(el) for el in obj])
        else:
            print(
                f"warning: unserializable data encountered.  using string representation: {obj}"
            )
            result = str(obj)
        return result

    @staticmethod
    def serialize_gd_to_py(obj):
        """Convert a GDScript object to a python object of list, tuple, dictionary, string"""

        result = {}
        if isinstance(obj, Dictionary) or isinstance(obj, dict):
            tmp = {}
            for k, v in obj.items():
                if isinstance(k, tuple):
                    tmp[k] = Conversions.serialize_gd_to_py(v)
                if isinstance(k, Vector3):
                    tmp[Conversions.vec3_to_tuple(k)] = Conversions.serialize_gd_to_py(
                        v
                    )
                else:
                    tmp[str(k)] = Conversions.serialize_gd_to_py(v)
            result = tmp
        elif isinstance(obj, Array) or isinstance(obj, list) or isinstance(obj, tuple):
            result = [Conversions.serialize_gd_to_py(el) for el in obj]
        elif isinstance(obj, Vector3):
            result = Conversions.vec3_to_tuple(obj)
        else:
            result = obj
        return result