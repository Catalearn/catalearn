import sys

class DummyModule(object):
    dummy = None

def import_all():
    sys.modules["gpu"] = DummyModule
    sys.modules["runners"] = DummyModule
    sys.modules["loggers"] = DummyModule
    sys.modules["global_params"] = DummyModule

def unimport_all():
    del sys.modules["gpu"]
    del sys.modules["runners"]
    del sys.modules["loggers"]
    del sys.modules["global_params"]
    del sys.modules["catalearn"]