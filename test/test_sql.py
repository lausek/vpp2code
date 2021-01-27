import pytest

from .deps import *

class TestSQL(Test):
    def test_er_diagram(self, diagrams, tmpdir):
        # copy file to tmpdir and change directory
        er_file = tmpdir.join('er-diagram.vpp')
        er_file.write_binary(diagrams['er'])
        os.chdir(tmpdir)

        args = Args(diagram='er-diagram.vpp', target='')

        vpp2code.run(args)

        print(tmpdir.join('online-pharmacy.sql').read())

        self.assertTrue(False)
