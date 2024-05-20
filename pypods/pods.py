"""
PyPods
Rohan Deshpande
"""

import sys
from os.path import exists, join
from subprocess import PIPE, Popen
from typing import Any, Dict, Optional

import pypods.ns as ns
from pypods.errors import PyPodNotStartedError, PyPodResponseError

from bson import dumps, loads


class PodLoader:
    """
    This class is for managing the lifecycle and interactions of a client with a specific pod.
    It loads and unloads pod functions into a namespace, sends data to the pod for processing,
    and handles responses and errors.
    """

    def __init__(self, pod_name: str, namespace: dict) -> None:
        """
        Initialize the PodLoader with the pod name and namespace.

        Args:
            pod_name (str): The name of the pod associated with this loader.
            namespace (dict): The namespace dictionary where pod functions are loaded.
        """
        self.pod_name = pod_name
        self.namespace = namespace
        self.loaded_functions = []

    def load_pod(self) -> None:
        """
        Load functions from the pod into the client's namespace.
        """
        pod_ns = ns.get_pod_namespace(self.pod_name)
        for function_name in pod_ns:
            args, kwargs = pod_ns[function_name]
            pod_function_name = self.create_a_function(function_name, *args, **kwargs)
            self.loaded_functions.append(pod_function_name)

    def unload_pod(self) -> None:
        """
        Unload functions loaded from the pod from the client's namespace.
        """
        for loaded_function in self.loaded_functions:
            del self.namespace[loaded_function]

    def send_data(self, data: bytes) -> None:
        """
        Send data to the pod for processing and handle the response.

        Args:
            data (bytes): The data to be sent to the pod.

        Returns:
            tuple: A tuple containing the stdout and stderr from the pod.
        """
        pod_interpreter = join("pods", f"{self.pod_name}", "venv", "bin", "python3")
        if not exists(pod_interpreter):
            raise PyPodNotStartedError("Pod interpreter is missing!")
        stdout, stderr = None, None
        with Popen(
            [pod_interpreter, "-m", f"pods.{self.pod_name}.pod_spec"],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
        ) as process:
            stdout, stderr = process.communicate(input=data)
        return stdout, stderr

    def create_a_function(self, func_name, *args, **kwargs) -> str:
        """
        Dynamically create a function that acts as a proxy for remote procedure calls to the pod.

        Args:
            func_name: The name of the function to be created.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            str: The name of the created function.
        """

        def rpc_proxy_function(*args, **kwargs):
            function_output = None
            try:
                function_dict = {"name": func_name, "args": args, "kwargs": kwargs}
                stdout, stderr = self.send_data(dumps(function_dict))
                if stderr:
                    error = loads(stderr)["error"]
                    raise PyPodResponseError(error)
                function_output = loads(stdout)["response"]
            except Exception as e:
                raise Exception(f"Unknown error: {e}")
            return function_output

        self.namespace[func_name] = rpc_proxy_function
        return func_name


class PodListener:
    """
    The PodListener class provides functionalities to interact with standard input and
    output streams, specifically tailored for handling serialized data in a structured format. It
    can read from stdin, write to stdout, and log errors to stderr, all using BSON serialization.
    """

    def __init__(self) -> None:
        pass

    def read_stdin(self) -> Optional[Dict[str, Any]]:
        """
        Read and deserialize data from standard input.

        Returns:
            Optional[Dict[str, Any]]: Parsed data if valid, None otherwise.
        """
        func_param = None
        try:
            data = sys.stdin.buffer.read()
            func_param = loads(data)
            if not isinstance(func_param, dict) or not {
                "name",
                "args",
                "kwargs",
            }.issubset(func_param):
                raise ValueError("Corrupt pod input!")
        except Exception as e:
            func_param = None
            self.write_stderr(str(e))
        return func_param

    def write_stdout(self, data: Any) -> None:
        """
        Serialize and write data to standard output.

        Args:
            data (Any): Data to be serialized and written.
        """
        try:
            bdata = dumps({"response": data})
            sys.stdout.buffer.write(bdata)
            sys.stdout.buffer.flush()
        except Exception as e:
            self.write_stderr(str(e))

    def write_stderr(self, error: str) -> None:
        """
        Serialize an error message and write it to standard error.

        Args:
            error (str): Error message to be serialized and written.
        """
        assert isinstance(error, str)
        sys.stderr.buffer.write(dumps({"error": error}))
        sys.stderr.flush()
