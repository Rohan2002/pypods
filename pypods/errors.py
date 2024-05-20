"""
PyPods
Rohan Deshpande
"""


class PyPodError(Exception):
    """Base class PyPodError"""

    pass


class PyPodNotStartedError(PyPodError):
    """Raised client pod tried to connect with a non-existant pod"""

    pass


class PyPodResponseError(PyPodError):
    """Raised when pod responds with an error"""

    pass

class PyPodNotFound(PyPodError):
    """Raised when pod could not be located"""

    pass