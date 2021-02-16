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
        init_args = [(get_ty(attr), attr.name) for attr in vp_class.attributes if is_uninitialized(attr)]

        src += '\n'
        src += '\t{} {}({}) {{\n'.format(VIS_PUBLIC, vp_class.name, ', '.join(map(lambda t: '%s %s' % t, init_args)))
        for _, init_arg_name in init_args:
            src += '\t\tthis.{n} = {n};\n'.format(n=init_arg_name)

        for own_attr in filter(lambda a: not a.kind.is_plain_association(), vp_class.attributes):
            src += '\t\tthis.{} = {};\n'.format(own_attr.name, get_initialize(own_attr))

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
        src += 'package {};\n'.format(vp_enum.package)
        src += '\n'
        src += '{} enum {} {{\n'.format(vp_enum.vis, vp_enum.name)
        src += ',\n'.join(map(lambda a: '\t' + a.name, vp_enum.attributes))
        src += '\n}\n'
        return src

    def generate_attribute(self, vp_attr):
        vis = get_visibility(vp_attr, default=VIS_PRIVATE)
        name, ty = vp_attr.name, get_ty(vp_attr)
        return "{} {} {};".format(vis, ty, name)

    def generate_operation(self, vp_operation):
        vis = get_visibility(vp_operation, default=VIS_PUBLIC)
        name, ret = vp_operation.name, map_type(vp_operation.ret)

        def to_ty_name(slot):
            return slot if isinstance(slot, str) else slot.name()

        params = ', '.join(map(lambda p: '{} {}'.format(to_ty_name(p[1]), p[0]), vp_operation.params))
        return "{} {} {}({}) {{}}".format(vis, ret, name, params)


def map_type(ty):
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
    return get_visibility(vp_attr) == VIS_PRIVATE and get_initialize(vp_attr) is None and vp_attr.kind.is_plain_association()


def get_initialize(vp_attr):
    if vp_attr.init is not None:
        return vp_attr.init.name()
    if vp_attr.mul is not None and vp_attr.mul.max != 1:
        if vp_attr.mul.max == '*':
            return 'new ArrayList<>()'
        return 'new {}[{}]'.format(vp_attr.get_ty_name(), vp_attr.mul.max)
    return 'new {}()'.format(vp_attr.get_ty_name())


def get_ty(vp_attr):
    if vp_attr.ty is None:
        return ''
    tys = vp_attr.get_ty_name()
    if vp_attr.mul is not None and vp_attr.mul.max != 1:
        if vp_attr.mul.max == '*':
            return 'List<{}>'.format(tys)
        return '{}[]'.format(tys)
    return tys
