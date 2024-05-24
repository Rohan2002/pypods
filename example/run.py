# Install all requirements defined in example/requirements.txt and execute python3 run.py
from pypods.pods import PodLoader

if __name__ == "__main__":
    pl = PodLoader("hello_world_pod", globals())
    pl.load_pod()  # Load pod's namespace
    print(hello_world_pod.foo(3, 4))
    pl.unload_pod()  # Unload pod's namespace()
