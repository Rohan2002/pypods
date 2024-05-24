from io import StringIO
import unittest
from unittest.mock import patch, MagicMock

from bson import dumps, loads
from pypods.pods import PodLoader, PodListener
from pypods.errors import PyPodResponseError
import json
import os
from os.path import join, exists
import shutil
import sys

class TestPodLoader(unittest.TestCase):
    @patch("pypods.pods.PodLoader.create_pod")
    @patch("pypods.pods.get_pod_namespace", return_value={"func1": ((), {})})
    @patch("pypods.pods.PodLoader.create_a_function")
    def test_load_pod(
        self,
        mock_create_a_function,
        mock_get_pod_namespace,
        mock_create_pod,
    ):
        pl_bad = PodLoader("123bad", {})
        with self.assertRaises(ValueError):
            pl_bad.load_pod()

        pl_good = PodLoader(pod_name="valid_pod", namespace={})
        pl_good.load_pod()

        self.assertIn("valid_pod", pl_good.namespace)
        self.assertIsNotNone(pl_good.namespace["valid_pod"])
        # Check args of mocked function
        mock_create_a_function.assert_called_once_with("func1", *(), **{})

    def test_unload_pod(self):
        pl_good = PodLoader("123bad", {"123bad": None})
        pl_good.unload_pod()
        self.assertTrue(len(pl_good.namespace) == 0)

        pl_bad = PodLoader("123bad", {"obj": None})
        pl_bad.unload_pod()
        self.assertTrue(len(pl_bad.namespace) != 0)

    # Integration test.
    # Create pod.
    # Load functions into a namespace from pod.
    # Call functions and check expected == actual output.
    # Unload functions from namespace.
    def test_pypod(self):
        pl = PodLoader(pod_name="test_pod", namespace={})
        root_dir = os.path.dirname(os.path.abspath(__file__))
        fixture_dir = join(root_dir, "fixtures")

        # Setup pod files
        shutil.copy(join(fixture_dir, "obj.json"), f"pods/{pl.pod_name}/obj.json")
        shutil.copy(join(fixture_dir, "pod.py"), f"pods/{pl.pod_name}/pod.py")

        self.assertTrue(exists(f"pods/{pl.pod_name}/obj.json"))
        self.assertTrue(exists(f"pods/{pl.pod_name}/pod.py"))

        # Create pod.
        # Load functions into a namespace from pod.
        pl.load_pod()

        # Call functions and check expected == actual output.
        test_pod_object = pl.namespace["test_pod"]
        foo_out = test_pod_object.foo1(1, 2)
        self.assertEqual(foo_out, 3)

        foo2_out = test_pod_object.foo2()
        self.assertEqual(foo2_out, "A")

        foo3_out = test_pod_object.foo3()
        expected = None
        with open(join(fixture_dir, "obj.json"), mode="r") as o:
            expected = json.load(o)
        self.assertEqual(foo3_out, expected)

        # Invalid function calls.
        with self.assertRaises(expected_exception=PyPodResponseError):
            foo2_bad_out = test_pod_object.foo2(
                "No-arg"
            )  # No arg should be provided for foo2

        with self.assertRaises(expected_exception=AttributeError):
            unknown_function_out = (
                test_pod_object.unknown_function()
            )  # Not avail function in pod's namespace

        # # Unload functions from namespace.
        pl.unload_pod()
        self.assertEqual(len(pl.namespace), 0)

class TestPodListener(unittest.TestCase):
    @patch('sys.stdin', new_callable=MagicMock)
    def test_read_stdin(self, mock_buffer):
        pod_listener = PodListener()
        mock_buffer.buffer.read.return_value = dumps({"name": "test", "args": [], "kwargs": {}})
        result = pod_listener.read_stdin()

        expected_result = {"name": "test", "args": [], "kwargs": {}}
        self.assertEqual(result, expected_result)
        
        # Corrupted stdin
        mock_buffer.buffer.read.return_value = dumps({"args": [], "kwargs": {}})
        result = pod_listener.read_stdin()
        self.assertEqual(result, None)
    @patch('sys.stdout.buffer.write')
    @patch('sys.stdout.buffer.flush')
    def test_write_stdout(self, mock_flush, mock_write):
        pod_listener = PodListener()
        test_data = {"key": "value"}
        expected_bson_data = dumps({"response": test_data})
        pod_listener.write_stdout(test_data)
        mock_write.assert_called_once_with(expected_bson_data)
        mock_flush.assert_called_once()
    
    @patch('sys.stderr.buffer.write')
    @patch('sys.stderr.buffer.flush')
    def test_write_stderr(self, mock_flush, mock_write):
        pod_listener = PodListener()
        err = "some-error-string"
        expected_bson_data = dumps({"error": err})
        pod_listener.write_stderr(err)
        mock_write.assert_called_once_with(expected_bson_data)
        mock_flush.assert_called_once()

if __name__ == "__main__":
    unittest.main()
