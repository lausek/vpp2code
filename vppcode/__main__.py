#!/usr/bin/python3

import os
import os.path
import sqlite3

from vp import parse

DIAGRAM = 'DIAGRAM'
DIAGRAM_ELEMENT = 'DIAGRAM_ELEMENT'
MODEL_ELEMENT = 'MODEL_ELEMENT'

JAVA_ENTITIES = ['Class']

def to_definition(b):
    """
    import json
    odd_vpp_format = b.decode('utf-8')
    odd_vpp_format.replace(';\r\n', ',')
    return json.loads(odd_vpp_format)
    """
    if not b is None:
        return b.decode('utf-8')


def get_class_diagrams(con):
    cur = con.cursor()
    cur.execute(
        """
        SELECT id FROM diagram
        WHERE diagram_type = 'ClassDiagram';
        """
    )
    return cur.fetchall()


def get_class_diagram_elements(con, diagram_id):
    cur = con.cursor()
    # using sqlite variable interpolation `?` delivers nothing...
    cur.execute(
        """
        SELECT shape_type, definition, model_element_id FROM diagram_element
        WHERE diagram_id = '{}'
        """
        .format(diagram_id)
    )
    return ((row[0], to_definition(row[1]), row[2]) for row in cur.fetchall())


def get_classes(con, model_id):
    cur = con.cursor()
    # using sqlite variable interpolation `?` delivers nothing...
    cur.execute(
        """
        SELECT id, name, definition
        FROM model_element
        WHERE id = '{}'
        AND model_type = 'Class'
        """
        .format(model_id)
    )
    return ((row[0], row[1], to_definition(row[2])) for row in cur.fetchall())


def get_connections(con, model_id):
    cur = con.cursor()
    # using sqlite variable interpolation `?` delivers nothing...
    cur.execute(
        """
        SELECT id, model_type, name, definition
        FROM model_element
        WHERE id = '{}'
        AND model_type IN ('Anchor', 'Association', 'Generalization')
        """
        .format(model_id)
    )
    return ((row[0], row[1], row[2], to_definition(row[3])) for row in cur.fetchall())

def get_model_element(con, model_id):
    cur = con.cursor()
    # using sqlite variable interpolation `?` delivers nothing...
    cur.execute(
        """
        SELECT id, model_type, name, definition
        FROM model_element
        WHERE id = '{}'
        """
        .format(model_id)
    )
    return ((row[0], row[1], row[2], to_definition(row[3])) for row in cur.fetchall())


def generate(model_items, target, package):
    import pathlib

    package_path = pathlib.Path(target, package.replace('.', '/'))
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

                # connections: anchor, association, generalization
                for mid, mty, mname, mdef in get_connections(con, model_id):
                    mobj = parse(mdef, mname, package)
                    print(mid, mty, mdef)

    generate(items, target_dir, package)

if __name__ == '__main__':
    main()
