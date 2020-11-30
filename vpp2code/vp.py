VIS_PUBLIC = 'public'
VIS_PRIVATE = 'private'
VIS_PROTECTED = 'protected'

def unquote(t):
    return t.strip()[1:-1]


def to_attr_name(t):
    return t[0].lower() + t[1:]


def parse(mdef, mname=None, package=None):
    if mdef.ty == 'Class':
        return parse_class(mdef, mname, package)

    if mdef.ty == 'Generalization':
        start = mdef.get('fromModel')
        end = mdef.get('toModel')
        return VpGeneralization(start, end)

    print(mdef.ty)
    assert False


def parse_class(mdef, mname=None, package=None):
    # check stereotypes: enumeration, interface (?)
    stereotypes = mdef.get('stereotypes', lambda sts: list(map(lambda s: s.name(), sts)))
    if stereotypes is not None and 'enumeration' in stereotypes:
        obj = VpEnum(mname, package)
    else:
        obj = VpClass(mname, package)

    # check if class is abstract
    is_abstract = mdef.get('abstract')
    if is_abstract is not None:
        obj.abstract = True

    # check associations
    tend = mdef.get('FromEndRelationships')
    if tend:
        for end in tend:
            end = end.cls().get('to')
            ty = end.get('type').name()
            mul = end.get('multiplicity', VpMultiplicity)

            attr = VpAttribute(name=to_attr_name(ty), ty=ty)
            attr.mul = mul
            obj.attributes.append(attr)

    # check attributes and operations
    child = mdef.get('Child')
    if child is not None:
        for item in child:
            if item.ty == 'Attribute':
                name = item.name
                vis = item.get('visibility')
                init = item.get('initialValue')
                ty = item.get('type')
                if ty is None:
                    ty = item.get('type_string', unquote)

                mul = item.get('multiplicity', VpMultiplicity)

                obj.attributes.append(VpAttribute(vis, name, ty, init, mul))

            if item.ty == 'Operation':
                op = VpOperation()

                op.name = item.name
                op.vis = item.get('visibility')

                def create_param(param):
                    ty = param.get('type')
                    if ty is None:
                        ty = item.get('type_string', unquote)

                    return param.name, ty

                params = item.get('Child')
                if params:
                    op.params = list(map(create_param, params))

                obj.operations.append(op)

    return obj


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
        init_args = []
        if self.attributes:
            init_args = [(attr.get_ty(), attr.name) for attr in self.attributes if attr.is_uninitialized()]

        src += '\n'
        src += '\t{} {}({}) {{\n'.format(VIS_PUBLIC, self.name, ', '.join(map(lambda t: '%s %s' % t, init_args)))
        for _, init_arg_name in init_args:
            src += '\t\tthis.{n} = {n};\n'.format(n=init_arg_name)
        src += '}\n'

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
    def __init__(self, vis=None, name=None, ty=None, init=None, mul=None):
        self.vis = vis
        self.name = name
        self.ty = ty
        self.init = init
        self.mul = mul

    def is_uninitialized(self):
        return self.get_vis() == VIS_PRIVATE and self.get_init() is None

    def get_ty_name(self):
        return self.ty if isinstance(self.ty, str) else self.ty.name()

    def get_init(self):
        if self.init is not None:
            return self.init.name()
        if self.mul is not None:
            if self.mul.max == 1:
                return # 'null'
            if self.mul.max == '*':
                return 'new ArrayList<>()'
            return 'new {}[{}]'.format(self.get_ty_name(), self.mul.max)

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
            assert self.name != 'Record'
            return VIS_PRIVATE
        return map_visibility(self.vis)

    def generate(self):
        vis = self.get_vis()
        name, ty, init = self.name, self.get_ty(), self.get_init()
        if init:
            return "{} {} {} = {};".format(vis, ty, name, init)
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
