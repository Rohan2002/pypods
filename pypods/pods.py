"""
PyPods
Rohan Deshpande
"""

import sys
import os
import shutil
import venv
from os.path import exists, join
from subprocess import PIPE, Popen, run
from typing import Any, Dict, Optional

from pypods.ns import *
from pypods.errors import PyPodNotStartedError, PyPodResponseError

from bson import dumps, loads

VENV_BIN = "Scripts" if os.name == 'nt' else "bin"
class PodLoader:
    """
    This class is for managing the lifecycle and interactions of a client with a specific pod.
    It loads and unloads pod functions into a namespace, sends data to the pod for processing,
    and handles responses and errors.
    """

    def __init__(self, pod_name: str, namespace: dict) -> None:
        """
        Initialize the PodLoader with the pod name and namespace.
        If the pod name does not exist in the file system, then it
        will be automatically created.

        Args:
            pod_name (str): The name of the pod associated with this loader.
            namespace (dict): The namespace dictionary where pod functions are loaded.
        """
        self.pod_name = pod_name
        self.namespace = namespace
        self.loaded_functions = []
        self.create_pod()

    def create_pod(self) -> None:
        """
        Create a new pod by setting up the necessary directory structure and dependencies.
        """
        # All pods are stored inside PODS_DIRECTORY
        # Create PODS_DIRECTORY if not exist and pod_name directory if not exist.
        pod_path = join(PODS_DIRECTORY, self.pod_name)
        if PODS_DIRECTORY not in os.listdir():
            print(f"Creating pods storage directory {PODS_DIRECTORY}...")
            os.makedirs(pod_path)
        elif self.pod_name not in os.listdir(PODS_DIRECTORY):
            print(f"Creating pod {self.pod_name} in pods storage...")
            os.mkdir(pod_path)

        pod_files = os.listdir(pod_path)
        if f"{PODS_CONFIG}.py" not in pod_files:
            print(f"Creating pod config file {PODS_CONFIG}.py...")
            pod_file = join(
                os.path.dirname(os.path.abspath(__file__)),
                "template",
                f"{PODS_CONFIG}.py",
            )
            shutil.copy(pod_file, pod_path)
        req_file = join(pod_path, "requirements.txt")
        if "requirements.txt" not in pod_files:
            print(f"Creating requirements.txt file...")
            with open(req_file, mode="w") as r:
                r.write(
                    "pypods"
                )  # Testing: -e /Users/rohandeshpande/applications/pods-project/python-pods
        gitignore_file = join(pod_path, ".gitignore")
        if ".gitignore" not in pod_files:
            print(f"Creating .gitignore file...")
            with open(gitignore_file, mode="w") as r:
                r.write(
                    "venv"
                )
        venv_dir = join(pod_path, "venv")
        if "venv" not in pod_files:
            print("Creating virtual environment inside pod...")
            venv.create(venv_dir, with_pip=True)
            print("Installing basic pod dependencies...")
            pip_executable = join(venv_dir, VENV_BIN, "pip")
            run(
                [
                    pip_executable,
                    "install",
                    "--disable-pip-version-check",
                    "-qr",
                    req_file,
                ]
            )

    def load_pod(self) -> None:
        """
        Load functions from the pod into the client's namespace.
        """
        pod_ns = get_pod_namespace(self.pod_name)
        for function_name in pod_ns:
            args, kwargs = pod_ns[function_name]
            pod_function_name = self.create_a_function(function_name, *args, **kwargs)
            self.loaded_functions.append(pod_function_name)

    def unload_pod(self) -> None:
        """
        Unload functions loaded from the pod from the client's namespace.
        """
        for loaded_function in self.loaded_functions:
            if loaded_function not in self.namespace:
                continue
            del self.namespace[loaded_function]

    def send_data(self, data: bytes) -> None:
        """
        Send data to the pod for processing and handle the response.

        Args:
            data (bytes): The data to be sent to the pod.

        Returns:
            tuple: A tuple containing the stdout and stderr from the pod.
        """
        if not isinstance(data, bytes):
            raise ValueError("data must be BSON serialized bytes")
        pod_interpreter = join(
            PODS_DIRECTORY, f"{self.pod_name}", "venv", VENV_BIN, "python3"
        )
        if not exists(pod_interpreter):
            raise PyPodNotStartedError("Pod interpreter is missing!")
        stdout, stderr = None, None
        with Popen(
            [pod_interpreter, "-m", f"{PODS_DIRECTORY}.{self.pod_name}.{PODS_CONFIG}"],
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
            except PyPodResponseError as e:
                raise PyPodResponseError(f"PyPodResponseError: {e}")
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
        if not isinstance(error, str):
            raise TypeError("Error message should be of type string.")
        sys.stderr.buffer.write(dumps({"error": error}))
        sys.stderr.flush()
