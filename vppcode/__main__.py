#!/usr/bin/python3

import sqlite3
import java

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


def get_model(con, model_id):
    cur = con.cursor()
    # using sqlite variable interpolation `?` delivers nothing...
    cur.execute(
        """
        SELECT name, model_type, definition
        FROM model_element
        WHERE id = '{}'
        OR parent_id = '{}'
        """
        .format(model_id, model_id)
    )
    return ((row[0], row[1], to_definition(row[2])) for row in cur.fetchall())


def generate(model_items):
    pass


def main():
    with sqlite3.connect('diagram.vpp') as con:
        model_items = {}

        for row in get_class_diagrams(con):
            diagram_id = row[0]
            print(">>> generating", diagram_id)

            elements = get_class_diagram_elements(con, diagram_id)

            for element in elements:
                # element
                ety, edef, model_id = element
                # model
                for mname, mty, mdef in get_model(con, model_id):
                    print(mname, mty, mdef)

                if mty in JAVA_ENTITIES:
                    pool[mname] = mdef

        generate(model_items)

if __name__ == '__main__':
    main()
