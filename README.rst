=======
porunga
=======

.. image:: https://secure.travis-ci.org/lukaszb/porunga.png?branch=master
  :target: http://travis-ci.org/lukaszb/porunga


``porunga`` is a tool for algorithms testing.


Installation
------------

In order to install ``porunga`` simply run::

    pip install porunga

Usage
-----

Basically we need specific files structure to test our algorithms::

    ./foobar/
    ./foobar/foobar.py
    ./foobar/testdata/
    ./foobar/testdata/test01.in
    ./foobar/testdata/test01.out
    ./foobar/testdata/test02.in
    ./foobar/testdata/test02.out
    ./foobar/testdata/test03.in
    ./foobar/testdata/test03.out

Here, ``foobar`` is our problem *name* - it should be same for parent the
directory and coded solution (here we have ``foobar.py`` but it can be other
language - see supported languages below; i.e. for Java we would create
``foobar.java`` file)

At ``./foobar/`` directory we would run::

    $ porunga test --lang python

See help for more options (you can see supported languages there too)::

    $ porunga test -h


Supported languages
-------------------

Currently ``porunga`` supports following languages:

- `C <http://en.wikipedia.org/wiki/C_(programming_language)>`_
- `C++ <http://www.cplusplus.com/>`_
- `Objective C <http://en.wikipedia.org/wiki/Objective-C>`_
- `Python <http://python.org>`_
- `Ruby <http://www.ruby-lang.org>`_
- `Java <http://en.wikipedia.org/wiki/Java_(programming_language)>`_

Java
----

Java source file should be named same as parent directory and should contain
public class with same name. So if our problem is called ``foobar`` we would
create ``foobar.java`` file with ``foobar`` named public class.

Tutorial
--------

Let's say we have a following problem to solve:

Problem
~~~~~~~

At input we get two integers: ``n``, ``m``, where ``1 <= n < m <= 100000``.
Your program should write to output all `Fibonacci numbers
<http://en.wikipedia.org/wiki/Fibonacci_number>`_ between ``n`` and ``m``
(including both). Numbers at output should be space separated.

Examples::

    INPUT  1: 3 5
    OUTPUT 1: 2 3 5

    INPUT  2: 6 10
    OUTPUT 2: 8 13 21 34 55

Firstly, let's make a directory for our solution::

    $ mkdir fibs
    $ cd fibs

Let's also create a ``testdata`` directory (exact name should be used) and put
there some test cases::

    $ mkdir testdata
    $ echo '3 5' > testdata/test01.in
    $ echo '2 3 5' > testdata/test01.out
    $ echo '6 10' > testdata/test02.in
    $ echo '8 13 21 34 55' > testdata/test02.out

Note that test inputs and outputs should have ``.in`` and ``.out`` extensions
respectively.

Now let's create our solution - we can pick any of the supported languages but
for sake of this tutorial let it be Python module. Create one (empty for now)::

    $ touch fibs.py

We should have following files created by now::

    ./fibs/
    ./fibs/fibs.py
    ./fibs/testdata/
    ./fibs/testdata/test01.in
    ./fibs/testdata/test01.out
    ./fibs/testdata/test02.in
    ./fibs/testdata/test02.out

That's it. We can now run ``porunga`` inside ``fibs`` directory and see our
solution being tested against created test cases::

    $ porunga test
    Testing ./fibs
    ==============

    => Binary: python /Users/lukasz/temp/fibs/fibs.py

    => Testing ./fibs/testdata/test01.in ... Fail
    => Testing ./fibs/testdata/test02.in ... Fail

    => Total time: 0.058s
    => 2 out of 2 tests failed

Well, we get 2 tests failed but we haven't actually coded anything yet. Just put
following code into ``fibs.py``::

    import fileinput
    import re
    import sys


    def fib(n):
        if n in (1, 2):
            return 1
        a = b = 1
        for x in range(3, n + 1):
            a, b = b, a + b
        return b

    def main():
        fin = fileinput.input()
        n, m = map(int, re.findall(r'\d+', fin.readline()))
        fibs = [str(fib(num)) for num in range(n, m + 1)]
        result = ' '.join(fibs)
        sys.stdout.write(result)


    if __name__ == '__main__':
        main()

(this is not optimal code as we compute Fibonacci numbers each time but it can
be easily upgraded)

Let's run tests again::

    $ porunga test
    Testing ./fibs
    ==============

    => Binary: python ./fibs/fibs.py

    => Testing ./fibs/testdata/test01.in ... OK [0.030]s
    => Testing ./fibs/testdata/test02.in ... OK [0.033]s

    => Total time: 0.063s
    => All 2 tests passed

