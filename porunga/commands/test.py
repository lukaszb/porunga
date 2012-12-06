from __future__ import print_function

import fnmatch
import os
import sys
from os import walk
from datetime import datetime
from glob import glob
from porunga.utils.backports import get_total_seconds
from monolith.cli import arg
from monolith.cli import SingleLabelCommand
from subprocess import Popen, PIPE
from termcolor import colored

joinpath = lambda *p: os.path.join(*p)
abspath = lambda *p: os.path.abspath(joinpath(*p))

LANGUAGES = {
    'python': {
        'fout': '{name}.py',
        'prog': 'python {fout}',
    },
    'ruby': {
        'fout': '{name}.rb',
        'prog': 'ruby {fout}',
    },
    'java': {
        'fin': '{name}.java',
        'fout': '{simplename}',
        'prog': 'java -cp {dirname} {fout}',
        'compiler': 'javac {fin}',
    },
    'objc': {
        'fin': '{name}.m',
        'fout': '{name}.m.out',
        'prog': '{fout}',
        'compiler': 'clang -ObjC -framework Foundation {fin} -o {fout}',
    },
    'c': {
        'fin': '{name}.c',
        'fout': '{name}.c.out',
        'prog': '{fout}',
        'compiler': 'gcc -O2 {fin} -o {fout}',
    },
    'cpp': {
        'fin': '{name}.cpp',
        'fout': '{name}.cpp.out',
        'prog': '{fout}',
        'compiler': 'g++ -O2 {fin} -o {fout}',
    },
}

def curdir():
    return os.path.curdir


class TestCommand(SingleLabelCommand):
    languages = LANGUAGES
    default_language = 'python'

    args = SingleLabelCommand.args + [
        arg('-l', '--lang', type=str, default=default_language,
            help='Available languages: %s (default: %s)' %
                (', '.join((key for key in sorted(languages.keys()))),
                 default_language) ),
        arg('-a', '--all', default=False, action='store_true'),
        arg('-v', '--verbose', default=False, action='store_true'),
        arg('-q', '--quiet', default=False, action='store_true'),
        arg('-c', '--case', type=str),
        arg('-t', '--timeout', type=float, default=3.0),
    ]

    def handle_label(self, label, namespace):
        self.namespace = namespace
        dirname = label or abspath(curdir())

        title = 'Testing %s' % dirname
        subtitle = '=' * len(title)
        self.success_continuation(title)
        self.success_continuation(subtitle)
        print()

        binary = self.get_binary(dirname, namespace.lang)
        self.info("Binary: %s" % binary)
        print()

        time = 0
        total = 0
        fails = 0
        for fin, fout in self.get_test_cases(dirname):
            total += 1
            info = self.test(dirname, binary, fin, fout)
            time += info['time']
            if not info['success']:
                fails += 1

        print()
        self.info("Total time: %.3fs" % time)
        if fails == 0:
            self.success('All %s tests passed' % total)
        else:
            self.error('%s out of %s tests failed' % (fails, total))

    def get_binary(self, dirname, lang):
        dirname = dirname.rstrip('/\\')
        if lang in LANGUAGES:
            data = {'dirname': dirname}
            info = LANGUAGES[lang]
            simplename = data['simplename'] = os.path.split(dirname)[1] # dirname
            name = joinpath(dirname, simplename)
            data['name'] = name
            fin = info['fin'].format(**data) if 'fin' in info else ''
            data['fin'] = fin
            fout = info['fout'].format(**data)
            data['fout'] = fout
            if 'compiler' in info:
                program = info['compiler'].format(**data)
                self.compile(program)
            return info['prog'].format(**data)
        else:
            self.exit("Wrong language specified")

    def test(self, dirname, binary, fin, fout):
        self.info("Testing %s ... " % fin, newline=False)
        start = datetime.now()
        prog = 'cat %s | %s' % (fin, binary)
        proc = Popen(prog, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = proc.communicate()
        result = out.strip()
        timedelta = datetime.now() - start

        prog2 = 'cat %s' % fout
        proc2 = Popen(prog2, stdout=PIPE, stderr=PIPE, shell=True)
        out2, err2 = proc2.communicate()
        expected = out2.strip()

        success = result == expected and proc.returncode == 0 and proc2.returncode == 0
        if success:
            self.success_continuation('OK [%.3f]s' % get_total_seconds(timedelta))
        else:
            self.error_continuation('Fail')
            if self.namespace.verbose:
                if proc.returncode != 0:
                    msg = "    Program returned with code %d:\n%s" % (
                        proc.returncode, err)
                else:
                    msg = "    Result was:\n%s\n but expected:\n%s\n" % (
                        result, expected)
                self.error_continuation(msg)

        return {
            'success': success,
            'time':get_total_seconds(timedelta),
        }

    def get_test_cases(self, dirname):
        if getattr(self.namespace, 'case', False):
            fins = [self.namespace.case]
        else:
            testdir = joinpath(dirname, 'testdata')

            suffix = '*.in'
            if self.namespace.all:
                fins = []
                for topdir, dirnames, filenames in walk(testdir):
                    fins.extend([joinpath(topdir, filename) for filename
                                 in fnmatch.filter(filenames, suffix)])
            else:
                fins = glob(joinpath(testdir, suffix))
        for fin in fins:
            yield fin, '.'.join(fin.split('.')[:-1] + ['out'])

    def compile(self, program):
        proc = Popen([program], stdout=PIPE, stderr=PIPE, shell=True)
        out, err = proc.communicate()
        if proc.returncode != 0:
            sys.stderr.write(err)
            self.exit("Error: compilation error! Tried command: %r" % program)

    def log(self, message, newline=True):
        if not self.namespace.quiet:
            print(message, end=newline and '\n' or '')

    def info(self, message, newline=True):
        text = colored(' => %s' % message, 'blue')
        self.log(text, newline)

    def info_continuation(self, message, newline=True):
        text = colored(message, 'blue')
        self.log(text, newline)

    def success(self, message, newline=True):
        text = colored(' => %s' % message, 'green')
        self.log(text, newline)

    def success_continuation(self, message, newline=True):
        text = colored(message, 'green')
        self.log(text, newline)

    def error(self, message, newline=True):
        text = ' => %s' % message
        self.error_continuation(text, newline)

    def error_continuation(self, message, newline=True):
        text = colored(message, 'red')
        self.log(text, newline)

    def exit(self, message, code=1):
        if not self.namespace.quiet:
            sys.stderr.write(colored('ERROR: ', 'red'))
            sys.stderr.write(colored(message, 'red'))
            sys.stderr.write('\n')
        sys.exit(code)


