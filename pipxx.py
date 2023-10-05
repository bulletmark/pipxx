#!/usr/bin/env python3
'Program to wrap pipx to add some extra functionality.'
# Author: Mark Blakeney, Sep 2023.

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional

HOMESTR = str(Path.home())
VMATCH = 'venvs are in '

def root_env() -> Dict[str, str]:
    'Return environment for root installs'
    env = os.environ.copy()
    for envvar, tdir in (('PIPX_BIN_DIR', '/usr/local/bin'),
                         ('PIPX_HOME', '/opt/pipx')):
        Path(tdir).mkdir(parents=True, exist_ok=True)
        env[envvar] = tdir
    return env

def unexpanduser(path: str) -> str:
    'Return string path with $HOME in string path substituted with ~'
    return path.replace(HOMESTR, '~', 1) \
            if path.startswith(HOMESTR) else path

def run(cmd: str) -> Optional[str]:
    'Run given shell command string'
    cmd += ' 2>/dev/null'
    try:
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                             universal_newlines=True)
    except Exception:
        return None

    if res.returncode != 0:
        return None

    return res.stdout and res.stdout.strip()

intercepts = {}
def intercept_cmd(func: Callable) -> None:
    intercepts[func.__name__[4:]] = func

@intercept_cmd
def cmd_list(cmds: List[str], env: Optional[Dict[str, str]]) -> bool:
    'Add some extra info to list command output'
    cmd = subprocess.Popen(cmds, stdout=subprocess.PIPE,
                           universal_newlines=True, env=env)
    bdir = None
    for line in (cmd.stdout or []):
        line = line.rstrip()
        if bdir:
            fields = line.split()
            if len(fields) > 1 and fields[0] == 'package':
                pkg = fields[1]
                jfile = bdir / pkg / 'pipx_metadata.json'
                with jfile.open() as fp:
                    data = json.load(fp)
                data = data.get('main_package', {})
                pkg = data.get('package', '')
                loc = unexpanduser(data.get('package_or_url', ''))
                if pkg and pkg == loc:
                    loc = f'package {loc}'

                if any(a in {'--editable', '-e'}
                        for a in data.get('pip_args', {})):
                    loc += ' (editable)'

                line += f' from {loc}'

        elif line.startswith(VMATCH):
            bdir = Path(line[len(VMATCH):].strip())

        print(line)
    return True

@intercept_cmd
def cmd_install(cmds: List[str], env: Optional[Dict[str, str]]) -> bool:
    'Inserts path to pyenv python executable if --python given'
    for opt in ('--python', '-P'):
        # Handle case where --python <path> is given as 2 option args
        if opt in cmds:
            index = cmds.index(opt)
            cmds[index] = '--python'
            index += 1
            version = cmds[index]
            arg = ''
        else:
            # Handle case where --python=<path> is given as a single
            # option arg
            for index, optstr in enumerate(cmds):
                if optstr.startswith(f'{opt}='):
                    _, version = optstr.split('=', 1)
                    arg = '--python='
                    break
            else:
                continue
        break
    else:
        return False

    # If given python program is a pyenv version then insert the pyenv
    # path to the executable
    pyenv_root = run('pyenv root')
    if pyenv_root:
        pyenv_version = run(f'pyenv latest {version}')
        if pyenv_version:
            pyexe_path = Path(pyenv_root, 'versions', pyenv_version,
                              'bin', 'python')
            if pyexe_path.exists():
                cmds[index] = arg + str(pyexe_path)

    return False

def main() -> Optional[int]:
    'Main code'
    # If invoked as root then set appropriate system directories for
    # installs
    env = root_env() if os.geteuid() == 0 else None

    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    cmdlist = f'pipx {cmd}'.split() + sys.argv[2:]

    # Intercept any commands we have reimplemented
    cmd = intercepts.get(cmd)
    if cmd and cmd(cmdlist, env):
        return 0

    return subprocess.run(cmdlist, env=env).returncode

if __name__ == '__main__':
    sys.exit(main())
