
import sys
import ast
import builtins
import dill
import os

def get_local_vars(source, namespace):

    # local_vars = sys._getframe(depth).f_locals

    local_vars_names = set(namespace.keys())

    root = ast.parse(source)

    required_vars_names = set()
    for node in ast.walk(root):
        if isinstance(node, ast.Name):
            required_vars_names.add(node.id)

    builtin_vars_names = set(vars(builtins).keys())

    required_local_vars = required_vars_names & local_vars_names

    # we might want to add a compiler-ish thing in the future 

    params = {}
    for v in required_local_vars:
        params[v] = namespace[v]

    return params
