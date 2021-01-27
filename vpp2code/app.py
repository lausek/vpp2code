import argparse
import os
import os.path

try:
    from .app import *
    from .backend import *
    from .db import *
    from .java import *
    from .sql import *
    from .vp import *

except ImportError:
    from app import *
    from backend import *
    from db import *
    from java import *
    from sql import *
    from vp import *

def generate(model_items, target):
    from pathlib import Path

    dispatchers = {
        'VpClass': JavaSourceGenerator(),
        'VpDatabase': SQLiteSourceGenerator(),
    }

    for mid, mobj in model_items.items():
        ty_name = type(mobj).__name__

        if ty_name not in dispatchers:
            print('cannot generate code for', ty_name, '. skipping...')
            continue
        
        dispatcher = dispatchers[ty_name]
        src = dispatcher.generate(mobj)
        fpath = Path(target, dispatcher.get_file_path(mobj))

        with open(fpath, 'w') as fout:
            fout.write(src)


def read(db_path, args):
    items = {}

    # open vpp database
    db = Database(db_path)

    # read all class diagrams
    class_diagrams = db.get_class_diagrams()
    if class_diagrams:
        classes = java_read(db, args, class_diagrams)
        if classes:
            items.update(classes)

    # read all entity relationship diagrams
    er_diagrams = db.get_entity_diagrams()
    if er_diagrams:
        sqls = er_read(db, args, er_diagrams)
        if sqls:
            items.update(sqls)

    return items


def run(args):
    items = read(args.diagram, args)
    generate(items, args.target)
