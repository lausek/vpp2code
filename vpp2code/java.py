try:
    from .vp import *

except ImportError:
    from vp import *

def java_read(db, args, class_diagrams):
    package = args.package
    items = {}

    for class_diagram in class_diagrams:
        diagram_id = class_diagram[0]
        print(">>> generating", diagram_id)

        for element in db.get_diagram_elements(diagram_id):
            # element
            ety, edef, model_id = element

            # classes
            for mid, mname, mdef in db.get_classes(model_id):
                mobj = parse(mdef, mname, package)
                items[mid] = mobj

            # connections: generalization
            for mid, mty, mname, mdef in db.get_connections(model_id):
                mobj = parse(mdef, mname, package)
                
                print(mobj.end.name(), '->', mobj.start.name())
                items[mobj.end.mid()].set_parent(mobj.start.name())

    return items

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
            kind = end.cls().get('from').get('aggregationKind')

            end = end.cls().get('to')
            ty = end.get('type').name()
            mul = end.get('multiplicity', VpMultiplicity)

            attr = VpAttribute(name=to_attr_name(ty), ty=ty)
            attr.mul = mul
            attr.kind = VpAggregationKind(kind)
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
