# vpp2code

generate java source code from vpp files.

``` bash
vpp2code diagram.vpp [--generate]
```

## Install

``` bash
git clone https://github.com/lausek/vpp2code
cd vpp2code
pip3 install .
```

## Testing

This project uses antlr4 to validate the programs output.

``` bash
curl -O https://www.antlr.org/download/antlr-4.9-complete.jar

# generate mysql lexer and parser (does not work :-)
java antlr-4.9-complete.jar -Dlanguage=Python3 test/antlr/mysql/SQLiteLexer.g4 test/antlr/mysql/SQLiteParser.g4

# generate java lexer and parser
java antlr-4.9-complete.jar -Dlanguage=Python3 test/antlr/java/JavaLexer.g4 test/antlr/java/JavaParser.g4

# generate mysql lexer and parser (does not work :-)
java antlr-4.9-complete.jar -Dlanguage=Python3 test/antlr/mysql/MySQLLexer.g4 test/antlr/mysql/MySQLParser.g4
```

> Note: The mysql and sqlite grammar files have been patched to avoid name conflicts with the generated python code.
