import os
import re

from pprint import pprint


def list_parent_dirs(path):
    """
    Return a list of the parents paths
    path treated as strings, must be absolute path
    """

    result = [path]

    was_relative = False
    path_abs = path
    pwd = None
    if not os.path.isabs(path):
        pwd = os.getcwd()
        path_abs = os.path.join(pwd, path)
        was_relative = True

    val = path_abs
    while val and val != os.sep:
        val = os.path.split(val)[0]
        result.append(val)

    if was_relative:
        return [os.path.relpath(path, start=pwd) for path in result]
    return result


def find_file_up(names, paths):
    """
    Find every files names in names list in
    every listed paths
    """
    assert isinstance(names, list), f"Names must be array, not: {type(names)}"
    assert isinstance(paths, list), f"Paths must be array, not: {type(names)}"
    
    result = []
    for path in paths:
        for name in names:
            file_path = os.path.join(path, name)
            if os.access(file_path, os.R_OK):
                result.append(file_path)

    return result


def uci2dict(payload, native_type=True):
    UCI_RGX = re.compile(r"^(?P<package>[^\.]+)\.((?P<new_section>[^\.=]+)|((?P<section_kind2>[^\.]+)\.(?P<name>[^\.=]+)))='?(?P<value>.*)'?$")

    ret = {}
    section_name = None
    for line in payload.split('\n'):

        m = UCI_RGX.match(line)
        if not m:
            continue
        m = m.groupdict()

        # Get name of the current scetion
        package = m['package']
        _section_name = m['new_section']
        is_section = False
        if _section_name:
            is_section = True
            section_name = _section_name
            section_kind = m['value']


        # Create structure
        if not package in ret:
            ret[package] = {}


        # Reparse section type:
        native_obj = 'dict'

        target = section_name
        if not is_section:
            target = m['section_kind2']

        if target.startswith('@'):
            tmp = re.match('@[^\[]+\[(?P<index>\d+)\]', target)
            section_name = tmp.groupdict('index')['index']
            if native_type:
                native_obj = 'list'


        # Handle container creation
        if not section_kind in ret[package]:
            if native_obj == 'dict':
                ret[package][section_kind] = {}
            else:
                ret[package][section_kind] = []


        if native_obj == 'dict':

            # Create container
            if not section_name in ret[package][section_kind]:
                ret[package][section_kind][section_name] = {}

            # Assign values:
            if not is_section:
                ret[package][section_kind][section_name][m['name']] =  m['value']

        else: # list
            index = int(section_name)

            # Create container
            if not index < len(ret[package][section_kind]):
                ret[package][section_kind].append({})

            # Assign values:
            if not is_section:
                ret[package][section_kind][index][m['name']] =  m['value']

    return ret



