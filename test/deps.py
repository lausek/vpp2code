from os.path import abspath, dirname, join

import os
import pytest
import sys

sys.path.insert(0, abspath(join(dirname(__file__), '..')))

import vpp2code

class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class Test:
    def assertIsInstance(self, obj, cls):
        self.assertTrue(isinstance(obj, cls))

    def assertEqual(self, expected, got):
        if expected == got:
            return
        print('expected', expected, ', got', got)
        self.assertTrue(False)

    def assertFalse(self, expr):
        self.assertTrue(not expr)

    def assertTrue(self, expr):
        assert expr

@pytest.fixture
def diagrams():
    from pathlib import Path
    test_root = Path(__file__).parent
    return {
        'er': open(test_root / 'er-diagram.vpp', 'rb').read(),
        'cls': open(test_root / 'cls-diagram.vpp', 'rb').read(),
    }

@pytest.fixture
def java_validator():
    try:
        from .antlr import JavaLexer, JavaParser
    except ImportError:
        from antlr import JavaLexer, JavaParser

    from antlr4.InputStream import InputStream
    import antlr4

    def inner(source):
        input_stream = InputStream(source)
        lexer = JavaLexer(input_stream)
        stream = antlr4.CommonTokenStream(lexer)
        parser = JavaParser(stream)
        tree = parser.compilationUnit()
        return tree is not None
    return inner

@pytest.fixture
def sqlite_validator():
    try:
        from .antlr import SQLiteLexer, SQLiteParser
    except ImportError:
        from .antlr import SQLiteLexer, SQLiteParser

    from antlr4.InputStream import InputStream
    import antlr4

    def inner(source):
        input_stream = InputStream(source)
        lexer = SQLiteLexer(input_stream)
        stream = antlr4.CommonTokenStream(lexer)
        parser = SQLiteParser(stream)
        tree = parser.sql_stmt_list()
        return tree is not None
    return inner
