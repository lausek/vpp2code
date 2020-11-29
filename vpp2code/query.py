import lark
from pathlib import Path

defparser = lark.Lark.open(Path(__file__).parent / 'defgrammar.lark')

class ModelObject:
    def __init__(self, speci, attrs):
        self.id = speci[0]
        self.what = speci[1]
        self.ty = speci[2]
        self.attrs = attrs

    def get(self, name, padfn=None):
        if not name in self.attrs:
            return None
        if not padfn is None:
            return padfn(self.attrs[name])
        return self.attrs[name]

    def __repr__(self):
        return '{}:{}({})'.format(self.id, self.ty, self.attrs)

def to_py(tree):
    if isinstance(tree, lark.Token):
        return str(tree)

    if tree.data == 'obj':
        d = {}
        speci = to_py(tree.children[0])
        for attr in tree.children[1:]:
            assert attr.data == 'attr'
            key, val = attr.children
            d[str(key)] = to_py(val)
        return ModelObject(speci, d)

    if tree.data == 'list':
        l = []
        for item in tree.children:
            l.append(to_py(item))
        return l

    if tree.data == 'attr':
        a, b = tree.children
        return (to_py(a), to_py(b))

    if 'ref' in tree.data:
        return ':'.join(tree.children)

    if tree.data == 'speci':
        a, b, c = tree.children
        return (to_py(a), to_py(b), to_py(c))

    assert False


def to_definition(b):
    if not b is None:
        src = b.decode('utf-8')

        parsesrc = src.replace('\t', '')
        tree = defparser.parse(parsesrc)
        val = to_py(tree.children[0])

        return val


def get_class_diagrams(con):
    cur = con.cursor()
    cur.execute(
        """
        SELECT id FROM diagram
        WHERE diagram_type = 'ClassDiagram';
        """
    )
    return cur.fetchall()


def get_class_diagram_elements(con, diagram_id):
    cur = con.cursor()
    # using sqlite variable interpolation `?` delivers nothing...
    cur.execute(
        """
        SELECT shape_type, definition, model_element_id FROM diagram_element
        WHERE diagram_id = '{}'
        """
        .format(diagram_id)
    )
    return ((row[0], to_definition(row[1]), row[2]) for row in cur.fetchall())


def get_classes(con, model_id):
    cur = con.cursor()
    # using sqlite variable interpolation `?` delivers nothing...
    cur.execute(
        """
        SELECT id, name, definition
        FROM model_element
        WHERE id = '{}'
        AND model_type = 'Class'
        """
        .format(model_id)
    )
    return ((row[0], row[1], to_definition(row[2])) for row in cur.fetchall())


def get_connections(con, model_id):
    cur = con.cursor()
    # using sqlite variable interpolation `?` delivers nothing...
    cur.execute(
        """
        SELECT id, model_type, name, definition
        FROM model_element
        WHERE id = '{}'
        AND model_type IN ('Association', 'Generalization')
        """
        .format(model_id)
    )
    return ((row[0], row[1], row[2], to_definition(row[3])) for row in cur.fetchall())

def get_model_element(con, model_id):
    cur = con.cursor()
    # using sqlite variable interpolation `?` delivers nothing...
    cur.execute(
        """
        SELECT id, model_type, name, definition
        FROM model_element
        WHERE id = '{}'
        """
        .format(model_id)
    )
    return ((row[0], row[1], row[2], to_definition(row[3])) for row in cur.fetchall())