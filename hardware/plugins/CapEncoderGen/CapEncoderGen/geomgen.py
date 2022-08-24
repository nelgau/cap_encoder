import os
import sys
import subprocess


from .logger import get_logger


class GeomgenCommand(object):
    def __init__(self):
        pass

    def run(self):
        command = ['poetry', 'run', 'python', '-m', 'geomgen.cli']

        env_command = ['env', '-u', 'PYTHONPATH', '-u', 'PYTHONHOME'] + command
        shell_command = ['zsh', '-lic', ' '.join(env_command)]
        working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'geomgen'))

        process = subprocess.Popen(shell_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_dir)

        out, err = process.communicate()
        return_code = process.poll()
        out = out.decode(sys.stdin.encoding)
        err = err.decode(sys.stdin.encoding)

        if return_code != 0:
            get_logger().info("error: %s", err)
            raise RuntimeError

        return out
