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
            mul = end.get('multiplicity')
            init = None

            attr = VpAttribute(name=to_attr_name(ty), ty=ty, init=init)
            obj.attributes.append(attr)

    # check attributes and operations
    child = mdef.get('Child')
    if child is not None:
        for item in child:
            if item.ty == 'Attribute':
                attr = VpAttribute()
                attr.name = item.name
                attr.vis = item.get('visibility')
                attr.init = item.get('initialValue')
                attr.ty = item.get('type')
                if attr.ty is None:
                    attr.ty = item.get('type_string', unquote)

                obj.attributes.append(attr)

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
        return 'public'
    if vis == 67:
        return 'protected'
    print(vis)
    assert False


class VpClass:
    def __init__(self, name, package):
        self.name = name.strip()
        self.package = package

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
            src += 'public abstract class {}'.format(self.name)
        else:
            src += 'public class {}'.format(self.name)

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
            init_args = ['{} {}'.format(attr.get_ty(), attr.name) for attr in self.attributes if
                         attr.get_vis() == 'private']

        src += '\n'
        src += '\tpublic {}({}) {{}}\n'.format(self.name, ', '.join(init_args))

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
        src += 'public enum {} {{\n'.format(self.name)
        src += ',\n'.join(map(lambda a: '\t' + a.name, self.attributes))
        src += '\n}\n'
        return src


class VpGeneralization:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class VpAttribute:
    def __init__(self, vis=None, name=None, ty=None, init=None):
        self.vis = vis
        self.name = name
        self.ty = ty
        self.init = init

    def get_init(self):
        if self.init is not None:
            return self.init.name()

    def get_ty(self):
        if self.ty is None:
            return ''
        if isinstance(self.ty, str):
            return self.ty
        return self.ty.name()

    def get_vis(self):
        if self.vis is None:
            assert self.name != 'Record'
            return 'private'
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
            return 'public'
        return map_visibility(self.vis)

    def generate(self):
        vis, name, ret = self.get_vis(), self.name, map_type(self.ret)
        params = ', '.join(map(lambda p: '{} {}'.format(p[1].name(), p[0]), self.params))
        return "{} {} {}({}) {{}}".format(vis, ret, name, params)
