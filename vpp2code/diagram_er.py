import logging

try:
    from .vp import *

except ImportError:
    from vp import *


def read_entities(db, args, entity_diagrams):
    items = {}

    for entity_diagram in entity_diagrams:
        diagram_id, name = entity_diagram
        vp_database = VpDatabase(name)

        logging.info(">>> generating %s", diagram_id)

        items[diagram_id] = vp_database

        for element in db.get_diagram_elements(diagram_id):
            # element
            ety, edef, model_id = element

            for mid, mname, mdef in db.get_entities(model_id):
                mobj = parse(vp_database, mdef)

    return items


def parse(vp_database, mdef):
    if mdef.ty == 'DBTable':
        return parse_table(vp_database, mdef)

    raise Exception('cannot parse type `{}`'.format(mdef.ty))


def parse_table(vp_database, mdef):
    table = vp_database.add_table(mdef.name)

    for column in mdef.get('Child'):
        name = column.name

        ty = column.get('type')
        ty = 'char' if ty is None else map_type(ty)

        length = column.get('length')
        is_primary = bool(column.get('primaryKey'))
        constraints = column.get('foreignKeyConstraints')

        vp_column = table.add_column(name, ty, length, is_primary)
        
        if constraints:
            for constraint in constraints:
                ref_column = constraint.get('refColumn').cls()
                foreign_key = constraint.get('foreignKey').cls()
                # referenced table
                from_model = foreign_key.get('fromModel').cls()
                # current table
                to_model = foreign_key.get('toModel').cls()

    return table

def map_type(ty):
    if ty == '11':
        return 'decimal'
    elif ty == '17':
        return 'date'
    elif ty == '27':
        return 'varchar'
    elif ty == '31':
        return 'integer'

    raise Exception('no type is known for `{}`'.format(ty))
