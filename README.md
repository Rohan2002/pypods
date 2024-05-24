# PyPods

A lightweight solution to execute Python dependencies in an isolated fashion.

This documentation will follow the classic philosophy of [A picture is worth a thousand words](https://en.wikipedia.org/wiki/A_picture_is_worth_a_thousand_words)

[![PyPI version](https://img.shields.io/pypi/v/pypods.svg)](https://pypi.org/project/pypods/)

# Problem
![problem](https://github.com/Rohan2002/pypods/blob/main/docs/imgs/problem.png?raw=true)

# Solution
![solution](https://github.com/Rohan2002/pypods/blob/main/docs/imgs/solution.png?raw=true)

# PyPod 🔎
![solution-magnified](https://github.com/Rohan2002/pypods/blob/main/docs/imgs/pypod.png?raw=true)

# Terminology
1. ```pods``` directory stores all the pods that will be used in the current project.
2. A ```pod``` is a container that contains its own Python interpreter, dependencies, and a ```pod.py``` file that exposes specific functions defined by the user.
3. A ```pod client``` is a file that calls the specific functions defined by the user.
4. A ```pod protocol``` is a way to exchange data between the pod and pod client. PyPods uses [binary json or bson](https://bsonspec.org/).

# How to use PyPods?

0. Optional step: Create a virtual environment in your project directory. ```python3 -m venv /path/to/venv``` and activate it via ```source /path/to/venv/bin/activate```.
1. Install pypods package via ```pip install pypods```
2. From the project's ```root``` directory, create a file and paste the following code.

Let's say the filename is ```client.py```
```python
# client.py will communicate with the hello_world_pod pod
from pypods.pods import PodLoader

# name of the pod, and namespace to inject pod's functions.
pl = PodLoader("hello_world_pod", globals())
pl.load_pod()   # Creates pod if not exist and then load pod namespace
pl.unload_pod() # Unload pod namespace
```

```python
from pypods.pods import PodLoader
```
This loads the PodLoader class that is designed for the pod client 
to communicate with the pod.

```python
pl = PodLoader(pod_name="hello_world_pod", namespace=globals())
```
PodLoader takes 2 arguements. 

```pod_name (str)```: The pod naming convention
should follow the rules of a python [identifier](https://docs.python.org/3/reference/lexical_analysis.html#identifiers).

```namespace (dict)```: All functions defined in the global scope of ```pod.py``` file will be injected into a ```namespace```. In this case, all functions defined in the global scope of ```pod.py``` are injected into ```client.py```'s global namespace.

```python
pl.load_pod()  # Creates pod if not exist and then load pod namespace
```

If ```hello_world_pod``` pod does not exist then ```load_pod()``` will create a
```hello_world_pod``` pod in the ```pods/``` directory.

Navigate to ```pods/hello_world_pod/``` directory and observe the file structure. This is the ```hello_world_pod```  pod.

```bash
hello_world_pod/
│
├── venv/
│   ├── bin/          (or Scripts/ on Windows)
│   ├── include/
│   ├── lib/
│   └── pyvenv.cfg
│
├── pod.py
├── requirements.txt
```

Important: ```pl.load_pod()``` will only load all functions defined in the global scope of the file ```pod.py``` file. Currently, we don't have any functions defined in pod.py file, so lets do that
from step 3. 

3. You can define functions inside a placeholder defined in the ```pod.py``` template file. Lets define the function ```foo```. Please don't change anything under  ```__name__ == "__main__"```. 

```python
# Template pod.py file inside the hello_world_pod pod.
"""
Write your module's functions in this area.
"""
def foo(x, y):
    return x + y

# Don't change anything here!
if __name__ == "__main__":
    from pypods.pods import PodListener
    pl = PodListener()  # PodListener will send output back to the pod client.
    msg = (
        pl.read_stdin()
    )  # Pod client writes function name and parameters to pod's stdin.
    if msg:
        # Unpack stdin to get function data
        function_name, args, kwargs = msg["name"], msg["args"], msg["kwargs"]
        try:
            # Check if function exists in pod module's namespace.
            # If yes, execute the function and send output back to the pod client.
            # If no, send error back to the pod client.
            if function_name in globals():
                function_output = globals()[function_name](*args, **kwargs)
                pl.write_stdout(function_output)
            else:
                pl.write_stderr(f"Function {function_name} does not exist in pod")
        except Exception as e:
            # Any error that occurs while calling the function is sent back to pod client.
            pl.write_stderr(str(e))
```
4. You can also create modules within the ```pods/hello_world_pod/``` directory and import it inside ```pod.py``` file. 

For example, let's say you create a module ```pods/hello_world_pod/module_test```. Inside module_test, you create a ```__init__.py``` file.
In this file you define the following function:

```python
def foo_in_module_test():
    return "foo_in_module_test"
```

Now inside ```pod.py``` you can import the function ```foo_in_module_test```.

```python
from pods.hello_world_pod.module_test import foo_in_module_test
```

Notice the function ```foo_in_module_test``` is defined in ```pod.py``` global namespace.

The ```pod.py``` file after adding ```foo_in_module_test```

```python
# Template pod.py file inside the hello_world_pod pod.
from pods.hello_world_pod.module_test import foo_in_module_test

"""
Write your module's functions in this area.
"""
def foo(x, y):
    return x + y

# Don't change anything here!
if __name__ == "__main__":
    from pypods.pods import PodListener
    ... # All stuff here 
```

5. Now lets look at our ```client.py``` file after adding the function ```foo``` in step 4 and importing the function ```foo_in_module_test``` from the module ```module_test``` in step 5.

```python
# client.py will communicate with the hello_world_pod pod
from pypods.pods import PodLoader

# name of the pod, and namespace to inject pod's functions.
pl = PodLoader("hello_world_pod", globals())
pl.load_pod()   # Load pod's namespace (This will now load the foo function).
foo_output = foo(1, 2) # Expected output = 1 + 2 = 3.
module_func_output = foo_in_module_test() # Expected output = "foo_in_module_test"
pl.unload_pod() # Unload pod's namespace
```

You ran a pod function ```foo``` and ```foo_in_module_test``` without importing it into the ```client.py``` file!

6. Finally it is good practice to call ```pl.unload_pod()``` to remove all pod functions from the client's namespace. It is a cleanup function.

See ```example/``` directory for a project example.

# Use cases of the library
1. If your project has a monolithic architecture, you can seperate your dependencies using PyPods!
2. If your project wants to test a library standalone then you can isolate it via PyPods.

# Author
Rohan Deshpande, PyPods 2024.
Inspired by the idea of [Babashka pods](https://github.com/babashka/pods).