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

        logging.info(">>> reading diagram %s", diagram_id)

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
        ty = 'integer' if ty is None else map_type(ty)
        logging.info('column %s %s %s', mdef.name, name, ty)

        length = column.get('length')
        is_primary = bool(column.get('primaryKey'))
        constraints = column.get('foreignKeyConstraints')

        vp_column = table.add_column(name, ty, length, is_primary)
        
        if constraints:
            # TODO: this is hacky but should work for most simple cases
            for constraint in constraints:
                ref_column = constraint.get('refColumn').cls()
                foreign_key = constraint.get('foreignKey').cls()
                # referenced table
                from_model = foreign_key.get('fromModel').cls()
                # current table
                #to_model = foreign_key.get('toModel').cls()

                on_update = map_constraint_method(foreign_key.get('onUpdate'))
                on_delete = map_constraint_method(foreign_key.get('onDelete'))

                ref_table = from_model.name

                for child in from_model.get('Child'):
                    if child.get('primaryKey') is not None:
                        vp_column.add_constraint(ref_table, [child.name], on_update, on_delete)

    return table


def map_type(ty):
    if ty == '11':
        return 'decimal'
    elif ty == '17':
        return 'date'
    elif ty == '27':
        return 'varchar'
    elif ty == '31':
        return 'char'

    raise Exception('no type is known for `{}`'.format(ty))


def map_constraint_method(method):
    if method is None or method == 'NULL':
        return 'CASCADE'

    raise Exception('constraint method `{}` is not supported'.format(method))
