VIS_PUBLIC = 'public'
VIS_PRIVATE = 'private'
VIS_PROTECTED = 'protected'

def unquote(t):
    return t.strip()[1:-1]


def to_attr_name(t):
    return t[0].lower() + t[1:]


def map_type(ty):
    if ty is None:
        return 'void'
    return ty


def map_visibility(vis):
    if vis is None:
        return ''
    vis = int(vis.lower())

    if vis == 71:
        return VIS_PUBLIC

    if vis == 67:
        return VIS_PROTECTED

    print(vis)
    assert False


class VpClass:
    def __init__(self, name, package):
        self.name = name.strip()
        self.package = package

        self.vis = VIS_PUBLIC
        self.parent = None
        self.abstract = False
        self.interfaces = []
        self.dependencies = []

        self.attributes = []
        self.operations = []

    def get_package_path(self):
        return '.'.join([self.package, self.name])

    def get_file_name(self):
        return '{}.java'.format(self.name)

    def get_file_path(self):
        from pathlib import Path

        package_path = Path(target, package.replace('.', '/'))
        package_path.mkdir(parents=True, exist_ok=True)

        return package_path / self.get_file_name()

    def set_parent(self, parent):
        self.parent = parent

    def generate(self):
        src = ''

        src += 'package {};\n'.format(self.package)

        if self.dependencies:
            src += '\n'
            for dependency in self.dependencies:
                src += 'import {};\n'.format(dependency.get_package_path())

        src += '\n'

        if self.abstract:
            src += '{} abstract class {}'.format(self.vis, self.name)
        else:
            src += '{} class {}'.format(self.vis, self.name)

        if self.parent is not None:
            src += ' extends {}'.format(self.parent)

        if self.interfaces:
            src += ' implements {}'.format(', '.join(self.interfaces))

        src += ' {\n'

        # attributes
        if self.attributes:
            src += '\n'
            for attr in self.attributes:
                src += '\t{}\n'.format(attr.generate())

        # constructor
        init_args = [(attr.get_ty(), attr.name) for attr in self.attributes if attr.is_uninitialized()]

        src += '\n'
        src += '\t{} {}({}) {{\n'.format(VIS_PUBLIC, self.name, ', '.join(map(lambda t: '%s %s' % t, init_args)))
        for _, init_arg_name in init_args:
            src += '\t\tthis.{n} = {n};\n'.format(n=init_arg_name)

        for own_attr in filter(lambda a: not a.kind.is_plain_association(), self.attributes):
            src += '\t\tthis.{} = {};\n'.format(own_attr.name, own_attr.get_init())

        src += '\t}\n'

        # operations
        if self.operations:
            src += '\n'
            for op in self.operations:
                src += '\t{}\n'.format(op.generate())

        src += '}\n'

        return src


class VpEnum(VpClass):
    def generate(self):
        src = ''
        src += 'package {};\n'.format(self.package)
        src += '\n'
        src += '{} enum {} {{\n'.format(self.vis, self.name)
        src += ',\n'.join(map(lambda a: '\t' + a.name, self.attributes))
        src += '\n}\n'
        return src


class VpGeneralization:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class VpAttribute:
    def __init__(self, vis=None, name=None, ty=None, init=None, mul=None, kind=None):
        self.vis = vis
        self.name = name
        self.ty = ty
        self.init = init
        self.mul = mul

        self.kind = VpAggregationKind(None) if kind is None else kind

    def is_uninitialized(self):
        return self.get_vis() == VIS_PRIVATE and self.get_init() is None and self.kind.is_plain_association()

    def get_ty_name(self):
        return self.ty if isinstance(self.ty, str) else self.ty.name()

    def get_init(self):
        if self.init is not None:
            return self.init.name()
        if self.mul is not None and self.mul.max != 1:
            if self.mul.max == '*':
                return 'new ArrayList<>()'
            return 'new {}[{}]'.format(self.get_ty_name(), self.mul.max)
        return 'new {}()'.format(self.get_ty_name())

    def get_ty(self):
        if self.ty is None:
            return ''
        tys = self.get_ty_name()
        if self.mul is not None and self.mul.max != 1:
            if self.mul.max == '*':
                return 'List<{}>'.format(tys)
            return '{}[]'.format(tys)
        return tys

    def get_vis(self):
        if self.vis is None:
            return VIS_PRIVATE
        return map_visibility(self.vis)

    def generate(self):
        vis, name, ty = self.get_vis(), self.name, self.get_ty()
        return "{} {} {};".format(vis, ty, name)


class VpOperation:
    def __init__(self, vis=None, name=None, ret=None):
        self.vis = vis
        self.name = name
        self.ret = ret
        self.params = []

    def get_vis(self):
        if self.vis is None:
            return VIS_PUBLIC
        return map_visibility(self.vis)

    def generate(self):
        vis, name, ret = self.get_vis(), self.name, map_type(self.ret)
        params = ', '.join(map(lambda p: '{} {}'.format(p[1].name(), p[0]), self.params))
        return "{} {} {}({}) {{}}".format(vis, ret, name, params)


class VpMultiplicity:
    def __init__(self, raw):
        self.min = None
        self.max = None

        if raw.startswith('"') and raw.endswith('"'):
            raw = unquote(raw)

        if '..' in raw:
            low, high = raw.split('..')
            self.min = int(low)
            self.max = int(high) if high != '*' else high
        else:
            self.max = int(raw)


# the aggregation is either:
# None -> association
# 66 -> aggregation
# 67 -> composition
class VpAggregationKind:
    def __init__(self, raw):
        self.kind = raw

    def is_plain_association(self):
        return self.kind is None


class VpDatabase:
    def __init__(self, name):
        self.name = name
        self.tables = []

    def get_file_name(self):
        return '{}.sql'.format(self.name)

    def get_file_path(self):
        return self.get_file_name()

    def generate(self):
        raise Exception('pls dont do this')

    def add_table(self, name):
        table = VpTable(name)
        self.tables.append(table)
        return table


class VpTable:
    def __init__(self, name):
        self.name = name
        self.columns = []

    def add_column(self, name, ty, length, is_primary=False):
        column = VpColumn(name, ty, length, is_primary)
        self.columns.append(column)
        return column


class VpColumn:
    def __init__(self, name, ty, length, is_primary=False):
        self.name = name
        self.ty = ty
        self.length = length
        self.is_primary = is_primary
        self.constraints = []

        assert self.ty

    def add_constraint(self):
        pass
