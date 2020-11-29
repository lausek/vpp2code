def unquote(t):
    return t.strip()[1:-1]


def parse(mdef, mname=None, package=None):
    if mdef.ty == 'Class':
        return parse_class(mdef, mname, package)

    if mdef.ty == 'Association':
        start = mdef.get('from')
        end = mdef.get('to')
        return VpAssociation(start, end)

    if mdef.ty == 'Generalization':
        start = mdef.get('fromModel')
        end = mdef.get('toModel')
        return VpGeneralization(start, end)

    print(mdef.ty)
    assert False


def parse_class(mdef, mname=None, package=None):
    obj = VpClass(mname, package)

    child = mdef.get('Child')
    if not child is None:
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
                    param.name

                    ty = param.get('type')
                    if ty is None:
                        ty = item.get('type_string', unquote)

                    return (param.name, ty)

                params = item.get('Child')
                if params:
                    op.params = list(map(create_param, params))
                
                obj.operations.append(op)

    return obj


class VpClass:
    def __init__(self, name, package):
        self.name = name
        self.package = package

        self.parent = None
        self.interfaces = []
        self.dependencies = []

        self.attributes = []
        self.operations = []


    def get_package_path(self):
        return '.'.join([package, self.name])


    def get_file_name(self):
        return '{}.java'.format(self.name)


    def set_parent(self, parent):
        self.parent = parent


    def generate(self):
        src = ''

        if self.dependencies:
            for dependency in self.dependencies:
                src += "import {};\n".format(dependency.get_package_path())

        src += 'public class {}'.format(self.name)

        if not self.parent is None:
            src += ' extends {}'.format(self.parent)

        if self.interfaces:
            src += ' implements {}'.format(', '.join(self.interfaces))

        src += " {\n"

        # attributes
        if self.attributes:
            src += "\n"
            for attr in self.attributes:
                src += "\t{}\n".format(attr.generate())

        # TODO: constructor

        # operations
        if self.operations:
            src += "\n"
            for op in self.operations:
                src += "\t{}\n".format(op.generate())

        src += "}\n"

        return src


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
        return 'private'
    print(vis)
    assert False


class VpAssociation:
    def __init__(self, left, right):
        self.left = left
        self.right = right


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
        if not self.init is None:
            return self.init.name()


    def get_ty(self):
        if self.ty is None:
            return ''
        if isinstance(self.ty, str):
            return self.ty
        return self.ty.name()


    def get_vis(self):
        return map_visibility(self.vis)


    def generate(self):
        vis = self.get_vis()
        name, ty, init = self.name, self.get_ty(), self.get_init()
        if init:
            return "{} {} {} = {};".format(vis, ty, name, init);
        return "{} {} {};".format(vis, ty, name);


class VpOperation:
    def __init__(self, vis=None, name=None, ret=None):
        self.vis = vis
        self.name = name
        self.ret = ret
        self.params = []


    def get_vis(self):
        return map_visibility(self.vis)


    def generate(self):
        vis, name, ret = self.get_vis(), self.name, map_type(self.ret)
        params = ', '.join(map(lambda p: '{} {}'.format(p[1].name(), p[0]), self.params))
        return "{} {} {}({}) {{}}".format(vis, ret, name, params);