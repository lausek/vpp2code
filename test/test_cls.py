import pytest

from .deps import *

class TestJava(Test):
    def test_cls_diagram(self, diagrams, tmpdir):
        # copy file to tmpdir and change directory
        cls_file = tmpdir.join('cls-diagram.vpp')
        cls_file.write_binary(diagrams['cls'])
        os.chdir(tmpdir)

        target_dir = tmpdir.join('de').join('vpp2code')
        args = Args(diagram='cls-diagram.vpp', target_dir='', java_package='de.vpp2code', generate=False)

        self.assertEqual(1, len(tmpdir.listdir()))

        vpp2code.run(args)

        self.assertEqual(1, len(tmpdir.listdir()))

    def test_cls_diagram_generate(self, diagrams, tmpdir, java_validator):
        # copy file to tmpdir and change directory
        cls_file = tmpdir.join('cls-diagram.vpp')
        cls_file.write_binary(diagrams['cls'])
        os.chdir(tmpdir)

        args = Args(diagram='cls-diagram.vpp', target_dir='', java_package='de.vpp2code', generate=True)

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

    def test_cls_diagram_generate2(self, diagrams, tmpdir, java_validator):
        # copy file to tmpdir and change directory
        cls_file = tmpdir.join('cls-diagram2.vpp')
        cls_file.write_binary(diagrams['cls2'])
        os.chdir(tmpdir)

        args = Args(diagram='cls-diagram2.vpp', target_dir='', java_package='de.vpp2code', generate=True)

        vpp2code.run(args)

        target_dir = tmpdir.join('de').join('vpp2code')

        run = False
        interface_found = False
        for generated_class in target_dir.listdir():
            print('testing', generated_class, '...')

            source = generated_class.read()
            print(source)

            if generated_class.basename.startswith('I'):
                interface_found = True
                assert 'interface' in source

            # source cannot be empty
            assert bool(source.strip())

            self.assertTrue(java_validator(source))
            run = True

        self.assertTrue(run)
        self.assertTrue(interface_found)
