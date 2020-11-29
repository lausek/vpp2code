#!/usr/bin/python3

import os
import os.path
import sqlite3

from pathlib import Path

try:
    from .query import *
    from .vp import parse

except ImportError:
    from query import *
    from vp import parse

DIAGRAM = 'DIAGRAM'
DIAGRAM_ELEMENT = 'DIAGRAM_ELEMENT'
MODEL_ELEMENT = 'MODEL_ELEMENT'

JAVA_ENTITIES = ['Class']

def generate(model_items, target, package):
    package_path = Path(target, package.replace('.', '/'))
    package_path.mkdir(parents=True, exist_ok=True)

    for mid, mobj in model_items.items():
        fname = mobj.get_file_name()
        fpath = package_path / fname

        with open(fpath, 'w') as fout:
            src = mobj.generate()
            fout.write(src)


def main():
    current_dir = os.getcwd()
    target_dir = os.path.join(current_dir, 'src')
    package = 'com.vppcode'
    items = {}

    with sqlite3.connect('diagram.vpp') as con:
        for row in get_class_diagrams(con):
            diagram_id = row[0]
            print(">>> generating", diagram_id)

            elements = get_class_diagram_elements(con, diagram_id)

            for element in elements:
                # element
                ety, edef, model_id = element

                # classes
                for mid, mname, mdef in get_classes(con, model_id):
                    mobj = parse(mdef, mname, package)
                    items[mid] = mobj

                # connections: association, generalization
                for mid, mty, mname, mdef in get_connections(con, model_id):
                    mobj = parse(mdef, mname, package)
                    #print(mid, mty, mdef)

    generate(items, target_dir, package)

if __name__ == '__main__':
    main()
