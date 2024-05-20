"""
PyPods
Rohan Deshpande
"""

import inspect
import importlib


def get_module_namespace(module_name):
    """
    Import a module by name and return its global namespace.

    Args:
        module_name (str): The name of the module to import.

    Returns:
        dict: The global namespace of the module.
    """
    try:
        module = importlib.import_module(module_name)
        return vars(module)
    except ModuleNotFoundError:
        print(f"Module '{module_name}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_pod_namespace(pod_name):
    """
    Get the functions within the pod's namespace.

    Args:
        pod_name (str): The name of the pod.

    Returns:
        dict: The namespace containing the function name as the key
        and function signature's parameters as the value.
    """
    pods_directory = "pods"
    pod_file = "pod_spec"
    module_name = f"{pods_directory}.{pod_name}.{pod_file}"
    module_ns = get_module_namespace(module_name)

    ns = {}
    for name, value in module_ns.items():
        if inspect.isfunction(value):
            function_parm = inspect.signature(value).parameters
            ar, kw = [], {}
            for _param in function_parm:
                _param_name = function_parm[_param].name
                if function_parm[_param].default == function_parm[_param].empty:
                    ar.append(_param_name)
                else:
                    kw[_param_name] = function_parm[_param].default

            ns[name] = (ar, kw)
    return ns
