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
    Provide some functions that may be common between project using libregice.

    In order to avoid code duplication, provide some functions to do common tasks
    such as configuring argparse arguments, allocating regice and loading SVD.
"""

import os
import sys

from argparse import ArgumentParser
from regicecommon.pkg import open_resource
from regicecommon.pkg import init_modules_args, process_modules_args
from svd import SVD, SVDText

def init_argument_parser(modules, device=None):
    """
        Initialize the argument parser

        This initializes the argument parser with common arguments.
        In addition, if modules name are provided, this also adds arguments from
        these modules.

        :param modules: A list of module name
        :param device: If not None, a Device object to initialize device
                       arguments.
        :return: An argument parser object
    """
    parser = ArgumentParser()
    if device:
        parser.add_argument('--help-device', action='store_true',
                            help='Print help for arguments specific to device')
    modules.append('libregice')
    init_modules_args(device, parser, modules)
    return parser

def process_arguments(parser, modules, device=None):
    """
        Parse and process the arguments

        This calls process_args for modules defining it.
        The modules could update a Device object, or return a dict with the
        values to return.
        There is no way to control in which order modules will be loaded,
        so nothing should be expected.
        :param parser: The argument parser object
        :param modules: A liste of module name
        :param device: If not None, a Device object to process device
                       arguments.
        :return: A tuple of device, parsed args and an dict with value returned
                 by modules.
    """
    if not device:
        args, unknown = parser.parse_known_args(sys.argv[1:])
        results = process_modules_args(None, args, ['libregice'])
        device = results['device']
    else:
        results = {}
        args = parser.parse_args(sys.argv[1:])
        if args.help_device:
            args = parser.parse_args(['-h'])

    results.update(process_modules_args(device, args, modules))
    return device, args, results

def load_svd(file):
    """
        Load the SVD file

        Load a SVD file. If the file name is a valid path, the function will
        load the file. Otherwise, the function will try to get the SVD file
        from package. If the function can't find a SVD file, this raises a
        FileNotFoundError error.

        :param file: The name of the file to open to load the SVD
    """
    try:
        if os.path.exists(file):
            svd = SVD(file)
        else:
            svd = SVDText(open_resource(None, file).read())
        svd.parse()
        return svd
    except OSError:
        raise FileNotFoundError
