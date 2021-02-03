class SQLiteSourceGenerator:
    def __init__(self):
        pass

    def get_target_output(self):
        return 'SQLite'

    def get_file_name(self, vp_object):
        assert type(vp_object).__name__ == 'VpDatabase'
        return '{}.sql'.format(vp_object.name)

    def get_file_path(self, vp_object):
        assert type(vp_object).__name__ == 'VpDatabase'
        return self.get_file_name(vp_object)

    def generate(self, vp_object):
        ty_name = type(vp_object).__name__

        if ty_name == 'VpDatabase':
            return self.generate_database(vp_object)
        elif ty_name == 'VpTable':
            return self.generate_table(vp_object)

        raise Exception('Cannot generate code from `{}`'.format(ty_name))

    def generate_database(self, vp_database):
        db_name = vp_database.name.replace('-', '_')

        src = 'DROP DATABASE IF EXISTS {};\n'.format(db_name)
        src += 'CREATE DATABASE {};\n'.format(db_name)
        src += 'USE {};\n'.format(db_name)

        for table in vp_database.tables:
            src += self.generate(table)

        return src

    def generate_table(self, vp_table):
        pk, table_body = [], []

        # declare columns
        for column in vp_table.columns:
            attrs = []

            # determine column type
            if column.length is None:
                ty = str(column.ty)
            else:
                ty = '{}({})'.format(column.ty, column.length)

            if column.is_primary:
                pk.append(column.name)

            table_body.append('\t{} {} {}'.format(column.name, ty, ' '.join(attrs)))

        # declare primary key
        if pk:
            table_body.append('\tPRIMARY KEY ({})'.format(', '.join(pk)))

        # declare foreign key constraints of columns
        for column in vp_table.columns:
            for constraint in column.constraints:
                constraint_name = 'FK_{}{}'.format(vp_table.name, constraint.ref_table)
                constraint_body = 'FOREIGN KEY ({}) REFERENCES {}({})\n\t\tON UPDATE {}\n\t\tON DELETE {}'.format(
                    ','.join(constraint.columns),
                    constraint.ref_table,
                    ','.join(constraint.ref_columns),
                    constraint.on_update,
                    constraint.on_delete,
                )
                table_body.append('\tCONSTRAINT {} {}'.format(constraint_name, constraint_body))

        src = 'CREATE TABLE {} (\n{}\n);\n'.format(vp_table.name, ',\n'.join(table_body))

        return src

