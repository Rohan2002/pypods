import sys
from os.path import exists, join
from subprocess import PIPE, Popen

import pypods.ns as ns
from pypods.errors import PyPodNotStartedError

from bson import dumps, loads
class PodLoader:
    def __init__(self, pod_name: str, namespace: dict) -> None:
        self.pod_name = pod_name
        self.namespace = namespace
        self.loaded_functions = []
    def load_pod(self):
        # Note pod_ns will only contain functions on the global scope of the pod.
        pod_ns = ns.get_pod_namespace(self.pod_name)
        for function_name in pod_ns:
            args, kwargs = pod_ns[function_name]
            pod_function_name = self.create_a_function(function_name, *args, **kwargs)
            self.loaded_functions.append(pod_function_name)
        
    def unload_pod(self):
        for loaded_function in self.loaded_functions:
            del self.namespace[loaded_function]
        
    def send_data(self, data):
        pod_interpreter = join("pods", f"{self.pod_name}","venv","bin","python3")
        if not exists(pod_interpreter):
            raise PyPodNotStartedError("Pod interpreter is missing!")
        stdout, stderr = None, None
        with Popen(
            [pod_interpreter, "-m", f"pods.{self.pod_name}.pod_spec"],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        ) as process:
            # Send data to the pod
            stdout, stderr = process.communicate(input=data)         
        return stdout, stderr

    def create_a_function(self, func_name, *args, **kwargs):
        # rpc_proxy_function acts as a client
        def rpc_proxy_function(*args, **kwargs):
            function_dict = {"name": func_name, "args": args, "kwargs": kwargs}
            response = self.send_data(dumps(function_dict))
            print(f"Response: {response}")
        self.namespace[func_name] = rpc_proxy_function
        return func_name

class PodListener:
    def __init__(self) -> None:
        pass
    def read_stdin(self):
        func_param = None
        try:
            data = sys.stdin.buffer.read()
            func_param = loads(data)
            if not isinstance(func_param, dict) or 'name' not in func_param or 'args' not in func_param or 'kwargs' not in func_param:
                raise ValueError("Corrupt pod input!")
            if func_param["name"] not in globals():
                function_name = func_param["name"]
                raise ValueError(f"Function {function_name} within pod does not exist!")
        except Exception as e:
            # TODO: test excepions in unit test. (ValueError)
            func_param = None
            self.write_stderr(e)
        return func_param

    def write_stdout(self, data):
        try:
            bdata = dumps(data)
            sys.stdout.buffer.write(bdata)
            sys.stdout.buffer.flush()
        except Exception as e:
            self.write_stderr(str(e))

    def write_stderr(self, error):
        assert type(error) == str
        sys.stderr.buffer.write(dumps({"error": error}))
        sys.stderr.flush()
