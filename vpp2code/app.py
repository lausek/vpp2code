import argparse
import logging
import os
import os.path

try:
    from .app import *
    from .backend import *
    from .db import *
    from .diagram_cl import *
    from .diagram_er import *
    from .vp import *

except ImportError:
    from app import *
    from backend import *
    from db import *
    from diagram_cl import *
    from diagram_er import *
    from vp import *


DISPATCHERS = {
    'VpClass': JavaSourceGenerator(),
    'VpEnum': JavaSourceGenerator(),
    'VpInterface': JavaSourceGenerator(),
    'VpDatabase': SQLiteSourceGenerator(),
}


def generate(args, model_items):
    from pathlib import Path

    # create target dir
    Path(args.target_dir).mkdir(parents=True, exist_ok=True)

    for mid, mobj in model_items.items():
        ty_name = type(mobj).__name__

        if ty_name not in DISPATCHERS:
            logging.info('cannot generate code for `%s`. skipping...', ty_name)
            continue
        
        dispatcher = DISPATCHERS[ty_name]
        src = dispatcher.generate(mobj)
        fpath = Path(args.target_dir, dispatcher.get_file_path(mobj))

        # create all folders
        fpath.parent.mkdir(parents=True, exist_ok=True)

        with open(fpath, 'w') as fout:
            fout.write(src)

        logging.info('generated file %s...', fpath)


def read(args, db_path):
    items = {}

    if not os.path.exists(db_path):
        raise Exception('file not found: {}'.format(db_path))

    # open vpp database
    db = Database(db_path)

    # read all class diagrams
    class_diagrams = db.get_class_diagrams()
    if class_diagrams:
        classes = read_classes(db, args, class_diagrams)
        if classes:
            items.update(classes)

    # read all entity relationship diagrams
    er_diagrams = db.get_entity_diagrams()
    if er_diagrams:
        sqls = read_entities(db, args, er_diagrams)
        if sqls:
            items.update(sqls)

    return items


def display(args, items):
    for item in items.values():
        ty_name = type(item).__name__

        if ty_name not in DISPATCHERS:
            logging.warning('cannot generate type `%s`. skipping...', ty_name)
            continue

        dispatcher_target_output = DISPATCHERS[ty_name].get_target_output()

        logging.info('## %s as %s\n', item.name, dispatcher_target_output)

        if args.verbose:
            dispatcher_target_src = DISPATCHERS[ty_name].generate(item)
            logging.info('%s', dispatcher_target_src)


def run(args):
    items = read(args, args.diagram)

    display(args, items)

    if args.generate:
        generate(args, items)
    else:
        logging.info('')
        logging.warning('no files were generated. add explicit parameter --generate instead.')
