import pypods.ns as ns

def load_pod(pod_name: str):
    pod_ns = ns.get_pod_namespace(pod_name)
    for function_name in pod_ns.items():
        args, kwargs = pod_ns[function_name]
        create_a_function(function_name, *args, **kwargs)
def create_a_function(func_name, *args, **kwargs):
    def rpc_proxy_function(*args, **kwargs):
        print(args)
        print(kwargs)
        print("RPC stuff")
    globals()[func_name] = rpc_proxy_function

if __name__ == "__main__":
    # args = ["a", "b"]
    # kwargs = {"c": None, "d": 1}
    # create_a_function("foo", *args, **kwargs)
    # # print(globals())
    # print(foo(1, 2))
    load_pod("test-pod")