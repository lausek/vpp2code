#!/usr/bin/python3

import argparse
import os
import os.path

try:
    from .app import *

except ImportError:
    from app import *


def main():
    import logging
    import sys

    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    current_dir = os.getcwd()
    default_target_dir = os.path.join(current_dir, 'src')

    parser = argparse.ArgumentParser(description='Convert visual paradigm diagrams into code')
    parser.add_argument('diagram', metavar='DIAGRAM', type=str, help='Path to the VP diagram file')

    parser.add_argument('--generate', default=False, action='store_true', help='Output directory of the resulting code')
    parser.add_argument('--target-dir', type=str, default=default_target_dir, help='Output directory of the resulting code')
    parser.add_argument('--verbose', default=False, action='store_true', help='Output generated source code')

    parser.add_argument('--java-package', type=str, default='com.vpp2code', help='Java package name to use as base')

    args = parser.parse_args()

    run(args)


if __name__ == '__main__':
    main()
