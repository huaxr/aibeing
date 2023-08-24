"""
This file contains the schema for the CodeBox API.
It is used to validate the data returned from the API.
It also helps with type hinting and provides a nice
interface for interacting with the API.
"""

from typing import Optional


class CodeBoxStatus():
    """
    Represents the status of a CodeBox instance.
    """
    def __init__(self, status: str) -> None:
        self.status = status

    def __str__(self):
        return self.status

    def __repr__(self):
        return f"Status({self.status})"

    def __eq__(self, other):
        return self.__str__() == other.__str__()


class CodeBoxOutput():
    """
    Represents the code execution output of a CodeBox instance.
    """
    def __init__(self, type: str, content: str) -> None:
        self.type = type
        self.content = content

    def __str__(self):
        return self.content

    def __repr__(self):
        return f"{self.type}({self.content})"

    def __eq__(self, other):
        return self.__str__() == other.__str__()


class CodeBoxFile():
    """
    Represents a file returned from a CodeBox instance.
    """
    def __init__(self, name: str, content: Optional[bytes] = None) -> None:
        self.name = name
        self.content = content

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"File({self.name})"
