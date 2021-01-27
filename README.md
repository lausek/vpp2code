# vpp2code

generate java source code from vpp files.

``` bash
vpp2code diagram.vpp
```

## Install

``` bash
git clone https://github.com/lausek/vppcode
cd vppcode
pip3 install .
```

## Testing

This project uses antlr4 to validate the programs output.

``` bash
curl -O https://www.antlr.org/download/antlr-4.9-complete.jar

# generate mysql lexer and parser
java antlr-4.9-complete.jar -Dlanguage=Python3 test/antlr/mysql/MySQLLexer.g4 test/antlr/mysql/MySQLParser.g4

# generate java lexer and parser
java antlr-4.9-complete.jar -Dlanguage=Python3 test/antlr/java/JavaLexer.g4 test/antlr/java/JavaParser.g4
```

> Note: The mysql grammar was patched to avoid name conflicts with the generated python code.
