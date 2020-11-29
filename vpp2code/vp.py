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
                vis = item.get('visibility')
                init_val = item.get('initialValue')
                ty = item.get('type')
                if ty is None:
                    ty = item.get('type_string', unquote)

                print(vis, ty, init_val)

            if item.ty == 'Operation':
                vis = item.get('visibility')

                params = item.get('Child')
                if params:
                    for param in params:
                        ty = param.get('type')
                        if ty is None:
                            ty = item.get('type_string', unquote)

    return obj


class VpClass:
    def __init__(self, name, package):
        self.name = name
        self.package = package

        self.parent = None
        self.interfaces = []
        self.dependencies = []

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

        # TODO: attributes

        # TODO: constructor

        # TODO: operations

        src += "}\n"

        return src


class VpAssociation:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class VpGeneralization:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class VpAttribute:
    pass


class VpOperation:
    pass