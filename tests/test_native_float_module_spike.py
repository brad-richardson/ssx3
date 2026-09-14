"""A private object replacement must preserve flags and production outputs."""
import unittest
from unittest.mock import patch
import shlex

from tools.native_float_module_spike import (
    BUILD, CHUNK, GENERATED, MODULE, ROOT, option_value, private_commands, recipes, strip_link_shell,
)


class NativeFloatModuleRecipeTests(unittest.TestCase):
    def fixture(self):
        output = ROOT/'local/research/private module fixture'
        original_object = 'CMakeFiles/module.dir/hot.c.o'
        compile_command = [
            '/usr/bin/clang', '-I'+str(GENERATED), '-O3', '-flto=thin', '-O2',
            '-ffp-contract=off', '-fno-fast-math', '-MD', '-MT', original_object,
            '-MF', original_object+'.d', '-o', original_object, '-c', str(CHUNK),
        ]
        link_command = [
            '/usr/bin/clang', '-O3', '-flto=thin', '-dynamiclib', '-o', MODULE.name,
            '-install_name', '@rpath/'+MODULE.name, 'CMakeFiles/module.dir/other.c.o',
            original_object, '-lm',
        ]
        return output, compile_command, link_command

    def test_replaces_only_one_object_and_private_paths(self):
        output, original_compile, original_link = self.fixture()
        before_compile, before_link = list(original_compile), list(original_link)
        compile_command, link_command = private_commands(output, original_compile, original_link)
        self.assertEqual(original_compile, before_compile)
        self.assertEqual(original_link, before_link)
        self.assertEqual(option_value(compile_command, '-o'), str(output/'chunk_0134.o'))
        self.assertEqual(option_value(compile_command, '-MF'), str(output/'chunk_0134.d'))
        self.assertEqual(option_value(compile_command, '-c'), str(output/'generated/chunks'/CHUNK.name))
        self.assertEqual(option_value(link_command, '-o'), str(output/MODULE.name))
        self.assertEqual([x for x in link_command if x.endswith('.o')], [
            str(BUILD/'CMakeFiles/module.dir/other.c.o'), str(output/'chunk_0134.o')])
        self.assertEqual(option_value(link_command, '-install_name'), '@rpath/'+MODULE.name)
        for flag in ('-O3', '-O2', '-flto=thin', '-ffp-contract=off', '-fno-fast-math'):
            self.assertEqual(compile_command.count(flag), original_compile.count(flag))

    def test_rejects_missing_or_duplicate_hot_object(self):
        output, compile_command, link_command = self.fixture()
        original_object = option_value(compile_command, '-o')
        for bad_link in ([x for x in link_command if x != original_object],
                         link_command+[original_object]):
            with self.assertRaisesRegex(ValueError, 'one hot-object'):
                private_commands(output, compile_command, bad_link)

    def test_rejects_output_outside_local_and_ambiguous_compile_outputs(self):
        output, compile_command, link_command = self.fixture()
        with self.assertRaisesRegex(ValueError, 'private output'):
            private_commands(ROOT/'native', compile_command, link_command)
        with self.assertRaisesRegex(ValueError, 'one argument'):
            private_commands(output, compile_command+['-o', 'another.o'], link_command)

    def test_shell_wrapper_is_removed_without_executing_other_operations(self):
        _, _, link = self.fixture()
        self.assertEqual(strip_link_shell([':', '&&', *link, '&&', ':']), link)
        for command in (link, [':', '&&', *link, '&&', 'unexpected', '&&', ':'],
                        [':', '&&', *link, ';', 'unexpected', '&&', ':']):
            with self.assertRaises(ValueError):
                strip_link_shell(command)

    def test_rpath_install_name_is_not_a_response_file(self):
        _, compile_command, link_command = self.fixture()
        output = '\n'.join((shlex.join(compile_command),
                            shlex.join([':', '&&', *link_command, '&&', ':'])))
        with patch('tools.native_float_module_spike.subprocess.check_output', return_value=output):
            self.assertEqual(recipes(), (compile_command, link_command))
        bad = output.replace(' -lm ', ' @unexpected.rsp -lm ')
        with patch('tools.native_float_module_spike.subprocess.check_output', return_value=bad):
            with self.assertRaisesRegex(ValueError, 'Response files'):
                recipes()


if __name__ == '__main__':
    unittest.main()
