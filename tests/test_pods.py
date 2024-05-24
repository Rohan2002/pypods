import unittest
from pypods.pods import PodLoader
from pypods.errors import PyPodResponseError
import json
import os
from os.path import join, exists
import shutil

# TODO: Unittest using mock, and patch functions for PodLoader and PodListener
class TestPodLoader(unittest.TestCase):
    def setUp(self) -> None:
        pass
    def test_load_pod(self):
        pass
    def test_unload_pod(self):
        pass
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
        foo_out = pl.namespace["foo1"](1, 2)
        self.assertEqual(foo_out, 3)
        
        foo2_out = pl.namespace["foo2"]()
        self.assertEqual(foo2_out, "A")

        foo3_out = pl.namespace["foo3"]()
        expected = None
        with open(join(fixture_dir, "obj.json"), mode="r") as o:
            expected = json.load(o)
        self.assertEqual(foo3_out, expected)

        # Invalid function calls.
        with self.assertRaises(expected_exception=PyPodResponseError):
            foo2_bad_out = pl.namespace["foo2"]("No-arg") # No arg should be provided for foo2
        
        # Unload functions from namespace.
        pl.unload_pod()
        self.assertEqual(len(pl.namespace), 0)

if __name__ == "__main__":
    unittest.main()