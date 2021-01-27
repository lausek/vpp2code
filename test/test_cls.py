import pytest

from .deps import *

class TestJava(Test):
    def test_er_diagram(self, diagrams, tmpdir, java_validator):
        # copy file to tmpdir and change directory
        er_file = tmpdir.join('cls-diagram.vpp')
        er_file.write_binary(diagrams['cls'])
        os.chdir(tmpdir)

        args = Args(diagram='cls-diagram.vpp', target='', package='de.vpp2code')

        vpp2code.run(args)

        target_dir = tmpdir.join('de').join('vpp2code')

        run = False
        for generated_class in target_dir.listdir():
            print('testing', generated_class, '...')
            source = generated_class.read()
            print(source)

            # source cannot be empty
            assert bool(source.strip())

            self.assertTrue(java_validator(source))
            run = True

        self.assertTrue(run)
