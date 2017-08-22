import sys
import json
import re
import os

def module_check(module_string, gpu_modules):
    matchObj = re.match( r'<module \'(.+)\' from', module_string)
    if matchObj is None:
        return None
    module_name = matchObj.group(1)
    if module_name in gpu_modules:
        return module_name
    return None

def class_check(module_string, gpu_modules):
    matchObj = re.match( r'<class \'(.+)\'>', module_string)
    if matchObj is None:
        return None
    class_location = matchObj.group(1)
    class_structure = class_location.split('.')

    if class_structure[0] in gpu_modules:
        return class_structure
    return None


def find_required_imports(source, local_vars):

    current_path = os.path.dirname(os.path.abspath(__file__))
    gpu_modules_path = os.path.join(current_path, 'resources/gpu_modules.json')
    with open(gpu_modules_path, 'r') as file:
        gpu_modules = json.load(file)

    import_commands = []
    unneeded_local_modules = []

    for var_name in local_vars:

        module_string = str(local_vars[var_name])

        module_name = module_check(module_string, gpu_modules)
        if module_name is not None:
            import_commands.append('import {} as {}'.format(module_name, var_name))
            unneeded_local_modules.append(var_name)
            continue

        class_structure = class_check(module_string, gpu_modules)
        if class_structure is not None:
            origin = '.'.join(class_structure[:-1])
            module = class_structure[-1]
            import_commands.append('from {} import {} as {}'.format(origin, module, var_name))
            unneeded_local_modules.append(var_name)
            continue

    return (import_commands, unneeded_local_modules)

