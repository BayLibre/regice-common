#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 BayLibre
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
    Provide some functions to deal with package resources.

    Regice is composed of many python modules.
    This provides common functions to manage all that modules,
    e.g. to load a module, or load files from a module.
"""

import importlib
import re

from pkg_resources import resource_isdir, resource_listdir, resource_stream
from pkg_resources import Requirement, iter_entry_points, DistributionNotFound
from pkgutil import iter_modules

def open_resource(module_name, fname):
    """
        Open a resource file

        This lookup for 'fname' in list of resources and open it if it exists.
        In the case where the resource doesn't exist, this raises OSError.

        :param module_name: Name of module where the resource is located.
                            Could be None if module name is unknown.
        :param fname: Name of the file to open. It could be a pattern.
        :return: A file object for the first resource matching with fname
    """
    if not module_name:
        for finder, name, ispkg in iter_modules():
            try:
                if 'regice' in name or 'Regice' in name:
                    return open_resource(name, fname)
            except OSError:
                continue
            except DistributionNotFound:
                continue
        raise OSError

    pkg = module_name.split('.')[0]
    files = get_resource_list(module_name, '/', '.*' + fname)
    if not files:
        raise OSError
    return resource_stream(pkg, files[0])

def get_resource_list(module_name, path, pattern=None):
    """
        Get a list of resources

        This finds the list of all files in package.
        This could be filtered using the pattern parameter.

        :param path: The root path where we want to get resources
        :param pattern: A pattern to filter resources
        :return: A list of resources
    """
    out = []
    pkg = module_name.split('.')[0]
    files = resource_listdir(pkg, path)
    for file in files:
        new_path = '{}/{}'.format(path, file)
        if resource_isdir(pkg, new_path):
            out += get_resource_list(module_name, new_path, pattern)
        else:
            if pattern is None or re.match(pattern, new_path):
                out.append(new_path)
    return out

def get_compatible_module(name):
    """
        Get a python module compatible with name

        This goes through a all Regice modules installed,
        and load and return the one that match with 'name' parameter.

        :param name: the name to match using is_compatible_with()
        :return: A python module or None if no compatible module is found
    """
    for entrypoint in iter_entry_points('regice'):
        if entrypoint.name == 'is_compatible_with':
            is_compatible_with = entrypoint.load()
            if is_compatible_with(name):
                return importlib.import_module(entrypoint.module_name)
    return None

def init_modules_args(parser, modules):
    """
        Initialize arguments parser with agrguments from modules

        Modules may provide arguments. This goes trhough all modules providing
        arguments and add them to arguments parser if that is required
        (listed in modules).

        :param modules: A list of modules name
    """
    if not modules:
        return

    for entrypoint in iter_entry_points('regice'):
        module_name = entrypoint.module_name.split('.')[0]
        if entrypoint.name == 'init_args' and module_name in modules:
            init_args = entrypoint.load()
            init_args(parser)
