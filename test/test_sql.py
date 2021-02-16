import pytest

from .deps import *

class TestSQL(Test):
    def test_er_diagram_sqlite(self, diagrams, tmpdir):
        # copy file to tmpdir and change directory
        er_file = tmpdir.join('er-diagram.vpp')
        er_file.write_binary(diagrams['er'])
        os.chdir(tmpdir)

        args = Args(diagram='er-diagram.vpp', target_dir='', generate=False)

        self.assertEqual(1, len(tmpdir.listdir()))

        vpp2code.run(args)

        self.assertEqual(1, len(tmpdir.listdir()))

    def test_er_diagram_sqlite_generate(self, diagrams, tmpdir, sqlite_validator):
        # copy file to tmpdir and change directory
        er_file = tmpdir.join('er-diagram.vpp')
        er_file.write_binary(diagrams['er'])
        os.chdir(tmpdir)

        args = Args(diagram='er-diagram.vpp', target_dir='', generate=True)

        vpp2code.run(args)

        run = False
        for sql_file in tmpdir.listdir():
            if not str(sql_file.realpath()).endswith('.sql'):
                continue

            print('testing', sql_file, '...')
            source = sql_file.read()
            print(source)

            # source cannot be empty
            assert bool(source.strip())

            self.assertTrue(sqlite_validator(source))
            run = True

        self.assertTrue(run)

    def test_er_diagram_sqlite_generate2(self, diagrams, tmpdir, sqlite_validator):
        # copy file to tmpdir and change directory
        er_file = tmpdir.join('er-diagram2.vpp')
        er_file.write_binary(diagrams['er2'])
        os.chdir(tmpdir)

        args = Args(diagram='er-diagram2.vpp', target_dir='', generate=True)

        vpp2code.run(args)

        run = False
        for sql_file in tmpdir.listdir():
            if not str(sql_file.realpath()).endswith('.sql'):
                continue

            print('testing', sql_file, '...')
            source = sql_file.read()
            print(source)

            # source cannot be empty
            assert bool(source.strip())

            self.assertTrue(sqlite_validator(source))
            run = True

        self.assertTrue(run)
