#!/usr/bin/python3

import argparse
import os
import os.path

try:
    from .db import *
    from .java import *
    from .sql import *
    from .vp import *

except ImportError:
    from db import *
    from java import *
    from sql import *
    from vp import *


DIAGRAM = 'DIAGRAM'
DIAGRAM_ELEMENT = 'DIAGRAM_ELEMENT'
MODEL_ELEMENT = 'MODEL_ELEMENT'


def generate(model_items, target):
    for mid, mobj in model_items.items():
        fpath = mobj.get_file_path()

        with open(fpath, 'w') as fout:
            src = mobj.generate()
            fout.write(src)


def read(db_path, args):
    items = {}

    db = Database(db_path)

    class_diagrams = db.get_class_diagrams()
    if class_diagrams:
        classes = java_read(db, args, class_diagrams)
        if classes:
            items.update(classes)

    er_diagrams = db.get_entity_diagrams()
    if er_diagrams:
        sqls = er_read(db, args, er_diagrams)
        if sqls:
            items.update(sqls)

    return items


def main():
    current_dir = os.getcwd()
    default_target_dir = os.path.join(current_dir, 'src')

    parser = argparse.ArgumentParser(description='convert visual paradigm diagrams to java code')
    parser.add_argument('diagram', metavar='DIAGRAM', type=str, help='path to the vp diagram file')
    parser.add_argument('--package', type=str, default='com.vpp2code', help='java package name to use as base')
    parser.add_argument('--target', type=str, default=default_target_dir, help='location for the resulting java code')

    args = parser.parse_args()

    items = read(args.diagram, args)
    generate(items, args.target)


if __name__ == '__main__':
    main()
