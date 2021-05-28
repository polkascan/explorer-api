#!/usr/bin/env python   1

import subprocess
import datetime


def execute_cmd(full_cmd, cwd=None):
    """Execute a git command"""

    process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    (stdoutdata, stderrdata) = process.communicate(None)
    if 0 != process.wait():
        raise Exception("Could not execute git command")

    return (stdoutdata.strip(), stderrdata.strip())


def get_hash():
    """Allow you to launch the script in command line with any hash"""
    return execute_cmd("git log -n 1 HEAD --pretty=format:\"%H\"")[0]


hash = get_hash()
with open("version.txt", mode='w') as file:
    file.write(f'{hash} -  {datetime.datetime.now()})
