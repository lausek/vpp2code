import argparse
import logging
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

def generate(args, model_items):
    from pathlib import Path

    dispatchers = {
        'VpClass': JavaSourceGenerator(),
        'VpEnum': JavaSourceGenerator(),
        'VpDatabase': SQLiteSourceGenerator(),
    }

    # create target dir
    Path(args.target).mkdir(parents=True, exist_ok=True)

    for mid, mobj in model_items.items():
        ty_name = type(mobj).__name__

        if ty_name not in dispatchers:
            logging.info('cannot generate code for `%s`. skipping...', ty_name)
            continue
        
        dispatcher = dispatchers[ty_name]
        src = dispatcher.generate(mobj)
        fpath = Path(args.target, dispatcher.get_file_path(mobj))

        # create all folders
        fpath.parent.mkdir(parents=True, exist_ok=True)

        with open(fpath, 'w') as fout:
            fout.write(src)

        logging.info('generated file %s...', fpath)


def read(args, db_path):
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
    items = read(args, args.diagram)
    generate(args, items)
