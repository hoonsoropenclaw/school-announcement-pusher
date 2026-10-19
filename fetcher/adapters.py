"""School announcement fetchers."""
from .school_a import SchoolAAdapter
from .school_b import SchoolBAdapter
from .school_c import SchoolCAdapter


def list_adapters():
    return [SchoolAAdapter(), SchoolBAdapter(), SchoolCAdapter()]
