def parse(mdef, mname=None, package=None):
    return VpClass(mname, package)


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


class VpGeneralization:
    pass


class VpAttribute:
    pass


class VpOperation:
    pass
