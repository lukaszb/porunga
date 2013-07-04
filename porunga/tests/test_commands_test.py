import os
import shutil
import sys
import tempfile
from argparse import Namespace
from porunga.commands.test import curdir
from porunga.commands.test import PorungaTestCommand
from porunga.utils.compat import unittest
from porunga.utils.paths import abspath
from mock import call
from mock import Mock
from mock import patch
from subprocess import PIPE
from termcolor import colored



class TestPorungaTestCommand(unittest.TestCase):

    def setUp(self):
        namespace = Namespace(quiet=True, all=False, lang='python', timeout=0)
        self.command = PorungaTestCommand()
        self.command.namespace = namespace
        self.command.namespace.verbose = True

    def test_get_binary(self):
        self.assertEqual(self.command.get_binary('foobar/', 'python'),
            'python foobar/foobar.py')

    def test_get_binary_in_subdirectory(self):
        self.assertEqual(self.command.get_binary('foobar/foo', 'python'),
            'python foobar/foo/foo.py')

    def test_get_binary_python(self):
        self.assertEqual(self.command.get_binary('foobar', 'python'),
            'python foobar/foobar.py')

    def test_get_binary_ruby(self):
        self.assertEqual(self.command.get_binary('foobar', 'ruby'),
            'ruby foobar/foobar.rb')

    def test_get_binary_java(self):
        self.command.compile = Mock()
        self.assertEqual(self.command.get_binary('foobar', 'java'),
            'java -cp foobar foobar')
        self.command.compile.assert_called_once_with('javac foobar/foobar.java')

    def test_get_binary_objc(self):
        self.command.compile = Mock()
        self.assertEqual(self.command.get_binary('foobar/', 'objc'),
            'foobar/foobar.m.out')
        self.command.compile.assert_called_once_with(
            'clang -ObjC -framework Foundation foobar/foobar.m -o foobar/foobar.m.out')

    def test_get_binary_c(self):
        self.command.compile = Mock()
        self.assertEqual(self.command.get_binary('foobar/', 'c'),
            'foobar/foobar.c.out')
        self.command.compile.assert_called_once_with(
            'gcc -O2 foobar/foobar.c -o foobar/foobar.c.out')

    def test_get_binary_cpp(self):
        self.command.compile = Mock()
        self.assertEqual(self.command.get_binary('foobar/', 'cpp'),
            'foobar/foobar.cpp.out')
        self.command.compile.assert_called_once_with(
            'g++ -O2 foobar/foobar.cpp -o foobar/foobar.cpp.out')

    # compile tests

    def test_compile_went_wrong(self):

        with patch('porunga.commands.test.Popen') as PopenMock:
            PopenMock.return_value = mock = Mock()
            mock.communicate = lambda: ('out', 'err')
            mock.returncode = 102
            with self.assertRaises(SystemExit) as err:
                self.command.compile('some prog')
                self.assertEqual(err.code, 102)

    def test_wrong_lang(self):
        with self.assertRaises(SystemExit):
            self.command.get_binary('foobar', 'foolang')

    def test_exit(self):
        with self.assertRaises(SystemExit) as err:
            self.command.exit('error message', 101)
            self.assertEqual(err.code, 101)

            self.command.namespace.quiet = False
            with patch.object(sys, 'stderr') as errmock:
                self.command.exit('message')
                self.assertEqual(errmock.write.call_args_list, [
                    call(colored('Error: ', 'red')),
                    call(colored('message', 'red')),
                    call('\n'),
                ])

    def test_get_test_cases_for_suffix(self):
        with patch('porunga.commands.test.glob') as mglob:
            mglob.return_value = ['foobar/test01.in', 'foobar/test02.in']
            cases = self.command.get_test_cases_for_suffix('foobar', 'in')
            self.assertItemsEqual(cases, [
                'foobar/test01.in',
                'foobar/test02.in',
            ])
            self.assertEqual(mglob.call_args, call('foobar/testdata/*.in'))

    def test_get_test_cases_for_suffix_all_flag(self):
        with patch('porunga.commands.test.walk') as walkmock:
            walkmock.return_value = [
                ('foobar/testdata', ['bigtests'], ['test01.in', 'test01.out', 'test02.in']),
                ('foobar/testdata/bigtests', [], ['test-big-01.in', 'test02.out']),
            ]
            self.command.namespace.all = True
            test_cases = self.command.get_test_cases_for_suffix('foobar/', 'in')

            walkmock.assert_called_once_with('foobar/testdata')
            self.assertEqual(test_cases, [
                'foobar/testdata/test01.in',
                'foobar/testdata/test02.in',
                'foobar/testdata/bigtests/test-big-01.in',
            ])

    def test_get_test_cases_with_case_option(self):
        self.command.namespace.case = '/foo/some.in'
        self.command.get_fout_name = Mock(return_value='/foo/some.out')
        cases = self.command.get_test_cases('foobar')
        self.assertEqual(cases, [('/foo/some.in', '/foo/some.out')])

    def test_get_test_cases(self):
        self.command.get_test_cases_for_suffix = Mock()
        self.command.get_test_cases_for_suffix.return_value = ['foo.in']
        self.command.get_fout_name = Mock(return_value='foo.out')
        result = self.command.get_test_cases('foobar')
        self.assertEqual(self.command.get_test_cases_for_suffix.call_args_list, [
            call('foobar', 'in'),
            call('foobar', 'IN'),
        ])
        self.assertEqual(result, [('foo.in', 'foo.out')])

    def test_get_test_cases_dupes_if_case_given(self):
        tempdir = tempfile.mkdtemp()
        testdir = abspath(tempdir, 'testdata')
        os.makedirs(testdir)
        fin = abspath(testdir, 'foo.in')
        fout = abspath(testdir, 'foo.out')
        open(fin, 'w')
        open(fout, 'w')
        self.command.namespace.case = fin
        cases = self.command.get_test_cases(tempdir)
        try:
            self.assertEqual(cases, [(fin, fout)])
        finally:
            shutil.rmtree(tempdir)

    def test_handle_label_error(self):
        with patch('porunga.commands.test.Popen') as PopenMock:
            self.command.get_test_cases = Mock(return_value=[
                ('test1.in', 'test1.out'), ('test2.in', 'test2.out')])
            mock = PopenMock.return_value = Mock()
            mock.communicate = lambda: ('out', 'err')
            mock.returncode = 0

            self.command.get_binary = Mock()
            self.command.info = Mock()
            self.command.error = Mock()

            self.command.handle_label('foobar', self.command.namespace)

            self.command.get_binary.assert_called_once_with('foobar', 'python')
            self.command.get_test_cases.assert_called_once_with('foobar')
            self.assertTrue(self.command.info.called)
            self.assertTrue(self.command.error.called) # out file does not exist

            # check if no label was given
            with patch('porunga.commands.test.curdir') as curdirmock:
                curdirmock.return_value = '/foo/bar'
                self.command.handle_label(None, self.command.namespace)
                self.assertEqual(self.command.get_binary.call_args,
                    call('/foo/bar', 'python'))

    def test_test_program(self):
        with patch('porunga.commands.test.Popen') as PopenMock:
            with tempfile.NamedTemporaryFile() as fout:
                fout.write(b'out')
                fout.flush()
                mock = PopenMock.return_value = Mock()
                mock.communicate = lambda: ('out', '')
                mock.returncode = 0
                info = self.command.test('foobar', 'foobar/foobar.out', 'fin', fout.name)

                self.assertEqual(PopenMock.call_args_list, [
                    call('cat fin | foobar/foobar.out', stdout=PIPE, stderr=PIPE,
                        shell=True),
                ])

                self.assertTrue(info['success'])
                self.assertIn('time', info)

    def test_test_program_fails(self):
        with patch('porunga.commands.test.Popen') as PopenMock:
            self.command.log = Mock()
            self.command.namespace.verbose = True
            mock = PopenMock.return_value = Mock()
            mock.communicate = lambda: ('out', 'err')
            mock.returncode = 1
            info = self.command.test('foobar', 'foobar/foobar.out', 'fin', 'fout')

            self.assertEqual(PopenMock.call_args_list, [
                call('cat fin | foobar/foobar.out', stdout=PIPE, stderr=PIPE,
                     shell=True),
            ])

            self.assertFalse(info['success'])
            self.assertIn('time', info)

    def test_logs(self):
        self.command.log = Mock()

        self.command.info('foo', False)
        self.assertEqual(self.command.log.call_args,
            call(colored(' => foo', 'blue'), False))

        self.command.info_continuation('foo', False)
        self.assertEqual(self.command.log.call_args,
            call(colored('foo', 'blue'), False))

        self.command.success('foo', False)
        self.assertEqual(self.command.log.call_args,
            call(colored(' => foo', 'green'), False))

        self.command.success_continuation('foo', False)
        self.assertEqual(self.command.log.call_args,
            call(colored('foo', 'green'), False))

        self.command.error('foo', False)
        self.assertEqual(self.command.log.call_args,
            call(colored(' => foo', 'red'), False))

        self.command.error_continuation('foo', False)
        self.assertEqual(self.command.log.call_args,
            call(colored('foo', 'red'), False))

    def test_curdir(self):
        with patch('porunga.commands.test.os') as osmock:
            osmock.path.curdir = '/foo/bar/baz'
            self.assertEqual(curdir(), '/foo/bar/baz')

