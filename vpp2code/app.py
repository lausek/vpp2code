import argparse
import os
import os.path

try:
    from .app import *
    from .db import *
    from .java import *
    from .sql import *
    from .vp import *

except ImportError:
    from app import *
    from db import *
    from java import *
    from sql import *
    from vp import *

def generate(model_items, target):
    from pathlib import Path

    for mid, mobj in model_items.items():
        fpath = Path(target, mobj.get_file_path())

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


def run(args):
    items = read(args.diagram, args)
    generate(items, args.target)
