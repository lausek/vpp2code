class SQLiteSourceGenerator:
    def __init__(self):
        pass

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
        src = 'CREATE DATABASE {};\n'.format(vp_database.name)
        src += 'USE DATABASE {};\n'.format(vp_database.name)

        for table in vp_database.tables:
            src += self.generate(table)

        return src

    def generate_table(self, vp_table):
        src = 'CREATE TABLE {} (\n'.format(vp_table.name)
        pk = []

        for column in vp_table.columns:
            ty = '{}({})'.format(column.ty, column.length)
            attrs = []

            if column.is_primary:
                pk.append(column.name)

            src += '\t{} {} {},\n'.format(column.name, ty, ' '.join(attrs))

        if pk:
            src += '\tPRIMARY KEY ({})\n'.format(', '.join(pk))

        src += ');\n'

        return src

