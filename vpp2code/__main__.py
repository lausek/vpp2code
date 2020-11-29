#!/usr/bin/python3

import os
import os.path

from pathlib import Path

try:
    from .db import *
    from .vp import *

except ImportError:
    from db import *
    from vp import *

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
    db_path = 'diagram.vpp'
    package = 'com.vppcode'
    items = {}

    db = Database(db_path)
    for row in db.get_class_diagrams():
        diagram_id = row[0]
        print(">>> generating", diagram_id)

        #print(get_model_element(con, 'XVC4Zq6GAqFkFRPc'))

        elements = db.get_class_diagram_elements(diagram_id)

        for element in elements:
            # element
            ety, edef, model_id = element

            # classes
            for mid, mname, mdef in db.get_classes(model_id):
                mobj = parse(mdef, mname, package)
                items[mid] = mobj

            # connections: association, generalization
            for mid, mty, mname, mdef in db.get_connections(model_id):
                mobj = parse(mdef, mname, package)
                
                if isinstance(mobj, VpAssociation):
                    pass
                else:
                    print(mobj.end.name(), '->', mobj.start.name())
                    items[mobj.end.mid()].set_parent(mobj.start.name())
                #print(items[mobj.start], '->', items[mobj.end])
                #print(mid, mty, mdef)

    generate(items, target_dir, package)

if __name__ == '__main__':
    main()
