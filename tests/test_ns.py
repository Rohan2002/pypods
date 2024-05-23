import unittest
from pypods.errors import PyPodNotFound
from pypods.ns import get_pod_namespace, get_module_namespace, PODS_DIRECTORY, PODS_CONFIG
class TestNamespace(unittest.TestCase):
    def test_get_pod_namespace(self):
        actual = get_pod_namespace("test-pod")
        expected = {'foo1': (['x', 'y'], {}), 'foo2': ([], {}), 'foo3': ([], {})}
        self.assertDictEqual(actual, expected)
    
    def test_import_module(self):
        module_name = f"{PODS_DIRECTORY}.test-pod.{PODS_CONFIG}"
        module_ns = get_module_namespace(module_name)
        self.assertTrue("foo1" in module_ns)
        self.assertTrue("foo2" in module_ns)
        self.assertTrue("foo3" in module_ns)
        
        with self.assertRaises(PyPodNotFound):
            module_name = f"{PODS_DIRECTORY}.test-asdfaspd.{PODS_CONFIG}"
            module_ns = get_module_namespace(module_name)
    
if __name__ == "__main__":
    unittest.main()