VIS_PUBLIC = 'public'
VIS_PRIVATE = 'private'
VIS_PROTECTED = 'protected'

def unquote(t):
    return t.strip()[1:-1]


def to_attr_name(t):
    return t[0].lower() + t[1:]


class VpClass:
    def __init__(self, name, package):
        self.name = name.strip()
        self.package = package.strip()

        self.vis = VIS_PUBLIC
        self.parent = None
        self.abstract = False
        self.interfaces = []
        self.dependencies = []

        self.attributes = []
        self.operations = []

    def set_parent(self, parent):
        self.parent = parent


class VpInterface(VpClass):
    pass


class VpEnum(VpClass):
    pass


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

    def get_ty_name(self):
        return self.ty if isinstance(self.ty, str) else self.ty.name()


class VpOperation:
    def __init__(self, vis=None, name=None, ret=None):
        self.vis = vis
        self.name = name
        self.ret = ret
        self.params = []


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

    def add_table(self, name):
        table = VpTable(name)
        self.tables.append(table)
        return table


class VpTable:
    def __init__(self, name):
        self.name = name
        self.columns = []

    def add_column(self, name, ty, length, is_primary=False, is_nullable=False):
        column = VpColumn(name, ty, length, is_primary, is_nullable)
        self.columns.append(column)
        return column


class VpColumn:
    def __init__(self, name, ty, length, is_primary=False, is_nullable=False):
        self.name = name
        self.ty = ty
        self.length = length
        self.is_primary = is_primary
        self.is_nullable = is_nullable
        self.constraints = []

        assert self.ty

    def add_constraint(self, ref_table, ref_columns, on_update=None, on_delete=None):
        columns = [self.name]
        self.constraints.append(VpConstraint(columns, ref_table, ref_columns, on_update, on_delete))


class VpConstraint:
    def __init__(self, columns, ref_table, ref_columns, on_update=None, on_delete=None):
        self.columns = columns
        self.ref_table = ref_table
        self.ref_columns = ref_columns
        self.on_update = on_update
        self.on_delete = on_delete

