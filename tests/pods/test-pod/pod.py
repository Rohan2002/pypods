# Template pod.py file
"""
Write your module's functions in this area.

If you have a class structure, make sure to put everything inside of
a function! See demo below.

class A:
    def __init__(self, x):
        self.x = x
    
    def get_x():
        return x

def function_x(x):
    a = A(5)
    return a.get_x()
"""
import json
import os

def foo1(x, y):
    return x + y

def foo2():
    return "A"

def foo3():   
    p = os.path.dirname(os.path.abspath(__file__))
    with open(f"{p}/obj.json", mode="r") as r:
        l = json.load(r)
    return l
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
