import lark
import sqlite3

from pathlib import Path

class Database:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.defparser = lark.Lark.open(Path(__file__).parent / 'defgrammar.lark')

    def to_py(self, tree):
        if isinstance(tree, lark.Token):
            return str(tree)

        if tree.data == 'obj':
            d = {}
            speci = self.to_py(tree.children[0])
            for attr in tree.children[1:]:
                assert attr.data == 'attr'
                key, val = attr.children
                d[str(key)] = self.to_py(val)
            return ModelObject(speci, d)

        if tree.data == 'list':
            l = []
            for item in tree.children:
                l.append(self.to_py(item))
            return l

        if tree.data == 'attr':
            a, b = tree.children
            return (self.to_py(a), self.to_py(b))

        if 'ref' in tree.data:
            return ModelRef(self, tree.children)

        if tree.data == 'speci':
            a, b, c = tree.children
            return (self.to_py(a), self.to_py(b), self.to_py(c))

        assert False


    def to_def(self, raw):
        if isinstance(raw, bytes):
            src = raw.decode('utf-8')

            parsesrc = src.replace('\t', '')
            tree = self.defparser.parse(parsesrc)
            val = self.to_py(tree.children[0])

            return val

        return raw


    def get_class_diagrams(self):
        cur = self.con.cursor()
        cur.execute(
            """
            SELECT id FROM diagram
            WHERE diagram_type = 'ClassDiagram';
            """
        )
        return cur.fetchall()


    def get_class_diagram_elements(self, diagram_id):
        cur = self.con.cursor()
        # using sqlite variable interpolation `?` delivers nothing...
        cur.execute(
            """
            SELECT shape_type, definition, model_element_id FROM diagram_element
            WHERE diagram_id = '{}'
            """
            .format(diagram_id)
        )
        return ((row[0], self.to_def(row[1]), row[2]) for row in cur.fetchall())


    def get_classes(self, model_id):
        cur = self.con.cursor()
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
        return ((row[0], row[1], self.to_def(row[2])) for row in cur.fetchall())


    def get_connections(self, model_id):
        cur = self.con.cursor()
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
        return ((row[0], row[1], row[2], self.to_def(row[3])) for row in cur.fetchall())

    def get_model_element(self, model_id):
        cur = self.con.cursor()
        # using sqlite variable interpolation `?` delivers nothing...
        cur.execute(
            """
            SELECT id, model_type, name, definition
            FROM model_element
            WHERE id = '{}'
            LIMIT 1
            """
            .format(model_id)
        )
        print(model_id)
        row = cur.fetchone()
        if not row is None:
            return (row[0], row[1], row[2], self.to_def(row[3]))


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


class ModelRef:
    def __init__(self, db, ids):
        self.db = db
        self.ids = ids

    def mid(self):
        return self.ids[-1]

    def name(self):
        nid = self.ids[-1]
        row = self.db.get_model_element(nid)
        if not row is None:
            return row[2]