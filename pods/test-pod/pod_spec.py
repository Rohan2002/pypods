from pprint import pprint

A_global = 5

def foo(a, b, c, d):
    return (a, b, c, d)

def foo2(a, b, c):
    return (a, b, c)

def foo3(a, b):
    return (a, b)

def foo4(a, b=None):
    return (a, b)

class A:
    def b():
        return "b"
    def a(a):
        return a
class B:
    def d():
        return "d"
    def c(c):
        return c
    