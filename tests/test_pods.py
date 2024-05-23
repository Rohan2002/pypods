import unittest
from pypods.pods import PodLoader, PodListener
from pypods.errors import PyPodResponseError
import json
from bson import dumps, loads
class TestPodLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.ns = {}
        self.pl = PodLoader(pod_name="test-pod", namespace=self.ns)
    def test_load_pod(self):
        self.pl.load_pod()

        self.assertTrue("foo1" in self.pl.namespace)
        self.assertTrue("foo2" in self.pl.namespace)
        
        # Make the functions from pod got replaced with rpc_proxy_functions
        self.assertTrue(self.pl.namespace["foo1"].__name__ == "rpc_proxy_function")
        self.assertTrue(self.pl.namespace["foo2"].__name__ == "rpc_proxy_function")
    def test_unload_pod(self):
        self.pl.load_pod()
        self.assertTrue(len(self.pl.namespace) != 0)
        self.pl.unload_pod()
        self.assertTrue(len(self.pl.namespace) == 0)

    # Integration test.
    # This will call load functions from pod, call them
    # and check if their output is correct and finally unload all the functions.
    def test_functions(self):
        self.pl.load_pod()
        foo_out = self.ns["foo1"](1, 2)
        self.assertEqual(foo_out, 3)
        
        foo2_out = self.ns["foo2"]()
        self.assertEqual(foo2_out, "A")

        foo3_out = self.ns["foo3"]()
        expected = None
        with open("fixtures/obj.json", mode="r") as o:
            expected = json.load(o)
        self.assertEqual(foo3_out, expected)

        with self.assertRaises(expected_exception=PyPodResponseError):
            foo2_bad_out = self.ns["foo2"]("No-arg") # No arg should be provided for foo2
        
        self.pl.unload_pod()

if __name__ == "__main__":
    unittest.main()