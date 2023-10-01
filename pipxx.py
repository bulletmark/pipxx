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
    if path.startswith(HOMESTR):
        path = path.replace(HOMESTR, '~', 1)
    return path

intercepts = {}
def intercept_cmd(func: Callable) -> None:
    intercepts[func.__name__[4:]] = func

@intercept_cmd
def cmd_list(cmds: List[str], env: Optional[Dict[str, str]]) -> None:
    'Add some extra info to list command output'
    cmd = subprocess.Popen(cmds, stdout=subprocess.PIPE, text=True, env=env)
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

def main() -> Optional[int]:
    'Main code'
    # If invoked as root then set appropriate system directories for
    # installs
    env = root_env() if os.geteuid() == 0 else None

    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    cmdlist = f'pipx {cmd}'.split() + sys.argv[2:]

    # Intercept any commands we have reimplemented
    cmd = intercepts.get(cmd)
    return cmd(cmdlist, env) if cmd \
            else subprocess.run(cmdlist, env=env).returncode

if __name__ == '__main__':
    sys.exit(main())
