#!/usr/bin/python3

import argparse
import os
import os.path

try:
    from .app import *

except ImportError:
    from app import *

#DIAGRAM = 'DIAGRAM'
#DIAGRAM_ELEMENT = 'DIAGRAM_ELEMENT'
#MODEL_ELEMENT = 'MODEL_ELEMENT'

def main():
    current_dir = os.getcwd()
    default_target_dir = os.path.join(current_dir, 'src')

    parser = argparse.ArgumentParser(description='convert visual paradigm diagrams to java code')
    parser.add_argument('diagram', metavar='DIAGRAM', type=str, help='path to the vp diagram file')
    parser.add_argument('--package', type=str, default='com.vpp2code', help='java package name to use as base')
    parser.add_argument('--target', type=str, default=default_target_dir, help='location for the resulting java code')

    args = parser.parse_args()

    app.run()


if __name__ == '__main__':
    main()
