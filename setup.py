#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2010-2020 Emmanuel Blot <emmanuel.blot@free.fr>
# Copyright (c) 2010-2016 Neotion
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Neotion nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL NEOTION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from codecs import open as codec_open
from os import close, unlink
from os.path import abspath, dirname, join as joinpath
from py_compile import compile as pycompile, PyCompileError
from re import split as resplit, search as research
from tempfile import mkstemp
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

#pylint: disable-msg=unused-variable


NAME = 'pyftdi'
PACKAGES = find_packages(where='.')
META_PATH = joinpath('pyftdi', '__init__.py')
KEYWORDS = ['driver', 'ftdi', 'usb', 'serial', 'spi', 'i2c', 'twi', 'rs232',
            'gpio', 'bit-bang']
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Other Environment',
    'Natural Language :: English',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: System :: Hardware :: Hardware Drivers',
]
INSTALL_REQUIRES = [
    'pyusb >= 1.0.0',
    'pyserial >= 3.0',
]
HERE = abspath(dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codec_open(joinpath(HERE, *parts), 'rb', 'utf-8') as dfp:
        return dfp.read()


def read_desc(*parts):
    """Read and filter long description
    """
    text = read(*parts)
    text = resplit(r'\.\.\sEOT', text)[0]
    return text


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = research(
        r"(?m)^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


class BuildPy(build_py):
    """Override byte-compile sequence to catch any syntax error issue.

       For some reason, distutils' byte-compile when it forks a sub-process
       to byte-compile a .py file into a .pyc does NOT check the success of
       the compilation. Therefore, any syntax error is explictly ignored,
       and no output file is generated. This ends up generating an incomplete
       package w/ a nevertheless successfull setup.py execution.

       Here, each Python file is build before invoking distutils, so that any
       syntax error is catched, raised and setup.py actually fails should this
       event arise.

       This step is critical to check that an unsupported syntax (for ex. 3.6
       syntax w/ a 3.5 interpreter) does not end into a 'valid' package from
       setuptools perspective...
    """

    def byte_compile(self, files):
        for file in files:
            if not file.endswith('.py'):
                continue
            pfd, pyc = mkstemp('.pyc')
            close(pfd)
            try:
                pycompile(file, pyc, doraise=True)
                continue
            except PyCompileError as exc:
                # avoid chaining exceptions
                pass
            finally:
                unlink(pyc)
            raise SyntaxError("Cannot byte-compile '%s'" % file)
        super().byte_compile(files)


if __name__ == '__main__':
    setup(
        cmdclass={'build_py': BuildPy},
        name=NAME,
        description=find_meta('description'),
        license=find_meta('license'),
        url=find_meta('uri'),
        version=find_meta('version'),
        author=find_meta('author'),
        author_email=find_meta('email'),
        maintainer=find_meta('author'),
        maintainer_email=find_meta('email'),
        keywords=KEYWORDS,
        long_description=read_desc('pyftdi/doc/index.rst'),
        packages=PACKAGES,
        scripts=['pyftdi/bin/i2cscan.py',
                 'pyftdi/bin/ftdi_urls.py',
                 'pyftdi/bin/ftconf.py'],
        package_dir={'': '.'},
        package_data={'pyftdi': ['*.rst', 'doc/*.rst', 'doc/api/*.rst',
                                 'INSTALL'],
                      'pyftdi.serialext': ['*.rst', 'doc/api/uart.rst']},
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        # tests requires >=3.6
        python_requires='>=3.5',
    )
