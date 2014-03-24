#!/usr/bin/env python
# Copyright 2014 University of Melbourne
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
import subprocess
import argparse


env = os.environ.copy()
line_match = re.compile(r'^([^\s]+):([\d]+):[\d]+: ')


def which(name, flags=os.X_OK):
    """taken from twisted/python/procutils.py"""
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                result.append(pext)
    return result

try:
    GIT = which('git')[0]
except:
    raise Exception('git executable can\'t be found')

try:
    FLAKE8 = which('flake8')[0]
except:
    raise Exception('flake8 executable can\'t be found')


def git_diff_linenumbers(filename, revision=None):
    """Return a list of lines that have been added/changed in a file."""
    diff_command = ['diff',
                    '--new-line-format="%dn "',
                    '--unchanged-line-format=""',
                    '--changed-group-format="%>"']
    difftool_command = ['difftool',
                        '-y', '-x', " ".join(diff_command)]

    def _call(*args):
        try:
            lines_output = subprocess.check_output(
                [GIT]
                + difftool_command
                + list(args)
                + ["--", filename],
                env=env)
        except subprocess.CalledProcessError:
            lines_output = ""
        return lines_output

    if revision:
        lines_output = _call(revision)
        return lines_output.split()
    else:
        lines_output = _call()
        # Check any files that are in the cache
        lines_output1 = _call("--cached")
        return lines_output.split() + lines_output1.split()


def flake8(filename, *args):
    """Run flake8 over a file and return the output"""
    proc = subprocess.Popen([FLAKE8, filename] + list(args),
                            stdout=subprocess.PIPE, env=env)
    (output, err) = proc.communicate()
    status = proc.wait()
    if status != 0 and len(output) == 0:
        print err
        raise Exception("Something odd happened while executing flake8.")
    return output


def git_changed_files(revision=None):
    """Return a list of all the files changed in git"""
    if revision:
        files = subprocess.check_output(
            [GIT, "diff", "--name-only", revision],
            env=env)
        return [filename for filename in files.split('\n')
                if filename]
    else:
        files = subprocess.check_output(
            [GIT, "diff", "--name-only"],
            env=env)
        cached_files = subprocess.check_output(
            [GIT, "diff", "--name-only", "--cached"],
            env=env)
        return [filename for filename
                in set(files.split('\n')) | set(cached_files.split('\n'))
                if filename]


def git_current_rev():
    return subprocess.check_output(
        [GIT, "rev-parse", "HEAD^"],
        env=env).strip()


WHITE_LIST = [re.compile(r'.*[.]py$')]
BLACK_LIST = []

SPECIAL_CASE_ARGS = {r'migrations/[0-9]+': ['--ignore=E501']}


def list_changed_files():
    files = git_changed_files()
    if not files:
        revision = git_current_rev()
        files = git_changed_files(revision)
    return files


def list_all_files():
    for root, directories, files in os.walk("karaage"):
        for filename in files:
            yield os.path.join(root, filename)


def main():
    parser = argparse.ArgumentParser(description='flake8 check of karaage')
    parser.add_argument("--changed", help="Only check changed files",
                        action="store_true")
    parser.add_argument("--verbose", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

    exit_status = 0
    revision = None
    if args.changed:
        revision = git_current_rev()
        files = list_changed_files()
    else:
        files = list_all_files()
    for filename in files:
        if not all(map(lambda x: x.match(filename),
                       WHITE_LIST)):
            if args.verbose:
                print >> sys.stderr, 'SKIPPING %s' % filename
            continue
        if any(map(lambda x: x.match(filename),
                   BLACK_LIST)):
            if args.verbose:
                print >> sys.stderr, 'SKIPPING %s' % filename
            continue

        if args.changed:
            included_lines = git_diff_linenumbers(filename, revision)

        if args.verbose:
            sys.stderr.write("Processing %s\n" % filename)

        for regex, flake_args in SPECIAL_CASE_ARGS.items():
            if re.search(regex, filename):
                flake8_output = flake8(filename, *flake_args)
                break
        else:
            flake8_output = flake8(filename)

        for line in flake8_output.split('\n'):
            line_details = line_match.match(line)
            if not line_details:
                continue
            flake_filename, lineno = line_details.groups()
            if not args.changed or lineno in included_lines:
                print line
                exit_status = 1
    sys.exit(exit_status)

if __name__ == "__main__":
    main()
