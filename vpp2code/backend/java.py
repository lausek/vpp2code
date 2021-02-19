VIS_PUBLIC = 'public'
VIS_PRIVATE = 'private'
VIS_PROTECTED = 'protected'


class JavaSourceGenerator:
    def __init__(self):
        pass

    def get_target_output(self):
        return 'Java'

    def get_package_path(self, vp_object):
        return '.'.join([vp_object.package, vp_object.name])

    def get_file_name(self, vp_object):
        return '{}.java'.format(vp_object.name)

    def get_file_path(self, vp_object):
        from pathlib import Path

        package_path = Path(vp_object.package.replace('.', '/'))

        return package_path / self.get_file_name(vp_object)

    def generate(self, vp_object):
        ty_name = type(vp_object).__name__

        if ty_name == 'VpClass':
            return self.generate_class(vp_object)

        elif ty_name == 'VpEnum':
            return self.generate_enum(vp_object)

        elif ty_name == 'VpInterface':
            return self.generate_interface(vp_object)

        raise Exception('Cannot generate code from `{}`'.format(ty_name))

    def generate_class(self, vp_class):
        src = ''

        if vp_class.package:
            src += 'package {};\n'.format(vp_class.package)

        if vp_class.dependencies:
            src += '\n'
            for dependency in vp_class.dependencies:
                src += 'import {};\n'.format(dependency.get_package_path())

        src += '\n'

        if vp_class.abstract:
            src += '{} abstract class {}'.format(vp_class.vis, vp_class.name)
        else:
            src += '{} class {}'.format(vp_class.vis, vp_class.name)

        if vp_class.parent is not None:
            src += ' extends {}'.format(vp_class.parent)

        if vp_class.interfaces:
            src += ' implements {}'.format(', '.join(vp_class.interfaces))

        src += ' {\n'

        # attributes
        if vp_class.attributes:
            src += '\n'
            for vp_attr in vp_class.attributes:
                src += '\t{}\n'.format(self.generate_attribute(vp_attr))

        # constructor
        init_args = [(get_attr_declare(attr), attr.name) for attr in vp_class.attributes if is_uninitialized(attr)]

        src += '\n'
        src += '\t{} {}({}) {{\n'.format(VIS_PUBLIC, vp_class.name, ', '.join(map(lambda t: '%s %s' % t, init_args)))
        for _, init_arg_name in init_args:
            src += '\t\tthis.{n} = {n};\n'.format(n=init_arg_name)

        for own_attr in filter(lambda a: not a.kind.is_plain_association(), vp_class.attributes):
            src += '\t\tthis.{} = {};\n'.format(own_attr.name, get_attr_initialize(own_attr))

        src += '\t}\n'

        # operations
        if vp_class.operations:
            src += '\n'
            for vp_operation in vp_class.operations:
                src += '\t{}\n'.format(self.generate_operation(vp_operation))

        src += '}\n'

        return src

    def generate_enum(self, vp_enum):
        src = ''

        if vp_enum.package:
            src += 'package {};\n'.format(vp_enum.package)

        src += '\n'
        src += '{} enum {} {{\n'.format(vp_enum.vis, vp_enum.name)
        src += ',\n'.join(map(lambda a: '\t' + a.name, vp_enum.attributes))
        src += '\n}\n'
        return src

    def generate_interface(self, vp_interface):
        src = ''

        if vp_interface.package:
            src += 'package {};\n'.format(vp_interface.package)

        src += '\n'
        src += '{} interface {} {{\n'.format(vp_interface.vis, vp_interface.name)

        if vp_interface.operations:
            src += '\n'
            for vp_operation in vp_interface.operations:
                src += '\t{}\n'.format(self.generate_operation(vp_operation, body=';'))

        src += '\n}\n'

        return src

    def generate_attribute(self, vp_attr):
        vis = get_visibility(vp_attr, default=VIS_PRIVATE)
        name, ty = vp_attr.name, get_attr_declare(vp_attr)
        return "{} {} {};".format(vis, ty, name)

    def generate_operation(self, vp_operation, body='{}'):
        vis = get_visibility(vp_operation, default=VIS_PUBLIC)
        name, ret = vp_operation.name, get_ty_return(vp_operation.ret)

        params = ', '.join(map(lambda p: '{} {}'.format(get_ty_declare(p[1]), p[0]), vp_operation.params))

        return '{} {} {}({}) {}'.format(vis, ret, name, params, body)


# if there is no return type -> return `void` as default
def get_ty_return(ty):
    if ty is None:
        return 'void'

    return ty


def get_visibility(item, default=''):
    if item.vis is None:
        return default

    vis = int(item.vis.lower())

    if vis == 71:
        return VIS_PUBLIC

    if vis == 67:
        return VIS_PROTECTED

    raise Exception('no visibility is known for `{}`'.format(vis))


def is_uninitialized(vp_attr):
    return get_visibility(vp_attr) == VIS_PRIVATE and get_attr_initialize(vp_attr) is None and vp_attr.kind.is_plain_association()


# initialize a class attribute. recognizes multiplicity.
def get_attr_initialize(vp_attr):
    if vp_attr.init is not None:
        return vp_attr.init.name()

    if vp_attr.mul is not None and vp_attr.mul.max != 1:
        if vp_attr.mul.max == '*':
            return 'new ArrayList<>()'
        return 'new {}[{}]'.format(get_ty_initialize(vp_attr.ty), vp_attr.mul.max)

    return 'new {}()'.format(get_ty_initialize(vp_attr.ty))


# translate a class attribute to java code. recognizes multiplicity.
def get_attr_declare(vp_attr):
    if vp_attr.ty is None:
        return ''

    ty_sig = get_ty_declare(vp_attr.ty)

    # check if we are talking about multiple types here
    if vp_attr.mul is not None and vp_attr.mul.max != 1:
        # variable amount of objects -> list
        if vp_attr.mul.max == '*':
            return 'List<{}>'.format(ty_sig)

        # fix amount of objects -> array
        return '{}[]'.format(ty_sig)

    return ty_sig


def get_ty_initialize(vp_type):
    return get_ty_declare(vp_type)


# takes a vp_type and makes it useable for declaration
def get_ty_declare(vp_type):
    # generate generic type declaration. supports recursive resolve.
    if vp_type.attrs:
        return '{}<{}>'.format(vp_type.name, ', '.join(map(get_ty_declare, vp_type.attrs)))

    return vp_type.name
