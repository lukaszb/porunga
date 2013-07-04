from __future__ import print_function
import datetime
import os
import subprocess
import tempfile
import threading
import time


class TimeoutExceeded(RuntimeError):
    pass


class Command(object):

    def __init__(self, cmd, stream=None, shell=False, timeout=None):
        self.cmd = cmd
        self.process = None
        self.thread = None
        self.returncode = None
        self.stream = stream or tempfile.NamedTemporaryFile()
        self.shell = shell
        self.timeout = timeout
        self.output = ''

    def __str__(self):
        return '<Command: %s | %r>' % (self.returncode, self.cmd)

    def run_in_thread(self):
        def target():
            self.process = subprocess.Popen(
                self.cmd,
                stdout=self.stream,
                stderr=subprocess.STDOUT,
                shell=self.shell,
            )
            self.process.communicate()
            self.returncode = self.process.returncode

        self.thread = threading.Thread(target=target)
        self.thread.start()
        return self.thread

    def iter_output_for_stream(self, stream, pause=0.05):
        """
        """
        afile = open(stream.name)
        thread = self.run_in_thread()
        start = datetime.datetime.now()

        def should_run():
            should = self.returncode is None
            if self.timeout:
                delta = (datetime.datetime.now() - start).total_seconds()
                should = should and delta < self.timeout
            return should

        # we need to run at least once as at this time as for very fast commands
        # process might already finish and returncode already set
        while True:
            if afile.tell() < os.path.getsize(afile.name):
                chunk = afile.read()
                self.output += chunk
                yield chunk
            if not should_run():
                break
            time.sleep(pause)

        if thread.is_alive():
            self.process.terminate()
            thread.join()
            raise TimeoutExceeded

    def iter_output(self, pause=0.05):
        """
        Returns iterator of chunked output.

        :param cmd: command that would be passed to ``subprocess.Popen``
        :param shell: Tells if process should be run within a shell. Default: False
        :param timeout: If command exceeds given ``timeout`` in seconds,
        ``TimeoutExceeded`` exception would be raised. Default: None
        :param pause: How long (in seconds) we should wait for the output.
        Default: 0.05

        Example::

            >>> command = Command('ls -l', shell=True)
            >>> for chunk in command.iter_output():
            ...     print(chunk, end='')
        """
        with self.stream as temp:
            for chunk in self.iter_output_for_stream(temp, pause=pause):
                yield chunk

    def run(self):
        for chunk in self.iter_output():
            pass # TimeoutExceeded might be thrown here
        return self.returncode


if __name__ == '__main__':
    cmd = 'for x in `seq 3`; do echo "Doing $x"; sleep 1; done'
    #cmd = 'echo foobar'
    timeout = 0.5
    command = Command(cmd, shell=True, timeout=timeout)
    try:
        for chunk in command.iter_output(pause=0.2):
            print(chunk, end='')
    except TimeoutExceeded as err:
        print(" -> Timeouted after %s" % timeout)
    print(" -> Command finished with returncode: %s" % command.returncode)

