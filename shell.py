from os import environ
from subprocess import run, Popen, PIPE


def run_process(args, *, output=True):
    if output:
        process = Popen(args)
        process.wait()
        environ['?'] = str(process.returncode)
        return None
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    output, err = process.communicate()
    environ['?'] = str(process.returncode)
    if err:
        print(err.decode())
    return [i for i in output.decode().split('\n')[:-1:]]