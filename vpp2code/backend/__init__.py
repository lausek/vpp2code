try:
    from java import JavaSourceGenerator
    from sqlite import SQLiteSourceGenerator
except ImportError:
    from .java import JavaSourceGenerator
    from .sqlite import SQLiteSourceGenerator
