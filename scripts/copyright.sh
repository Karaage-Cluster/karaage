#!env python
import argparse
import os

parser = argparse.ArgumentParser(description='Process copyright in Python.')
parser.add_argument('files', nargs='+', help='Files to process')
args = parser.parse_args()

for in_filename in args.files:
    out_filename = in_filename + ".tmp"

    with open(in_filename, "r") as in_file:
        with open(out_filename, "w") as out_file:
            got_copyright = False
            for line in in_file:
                if line.startswith('# Copyright'):
                    got_copyright = True
                elif line == "#\n" and got_copyright:
#                    out_file.write(
#                        "# Copyright 2010-2017, The University of Melbourne\n")
                    out_file.write(
                        "# Copyright 2013-2017, Brian May\n")
                    out_file.write("#\n")
                    got_copyright = False
                else:
                    out_file.write(line)

    os.rename(out_filename, in_filename)
