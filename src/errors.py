class PyPodError(Exception):
    """Base class PyPodError"""
    pass

class PyPodNotStartedError(PyPodError):
    """Raised client pod tried to connect with a non-existant pod"""
    pass