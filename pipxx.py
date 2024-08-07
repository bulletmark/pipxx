#!/usr/bin/env python3
'Program to wrap pipx to add some extra functionality.'
# Author: Mark Blakeney, Sep 2023.

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Iterator

HOME = Path.home()
VMATCH = 'venvs are in '

def root_env() -> dict[str, str]:
    'Return environment for root installs'
    env = os.environ.copy()
    for envvar, tdir in (('PIPX_BIN_DIR', '/usr/local/bin'),
                         ('PIPX_MAN_DIR', '/usr/local/share/man'),
                         ('PIPX_HOME', '/opt/pipx')):
        if envvar not in env:
            env[envvar] = tdir
    return env

def unexpanduser(path: str | Path) -> str:
    'Return path name, with $HOME replaced by ~ (opposite of Path.expanduser())'
    ppath = Path(path)

    if ppath.parts[:len(HOME.parts)] != HOME.parts:
        return str(path)

    return str(Path('~', *ppath.parts[len(HOME.parts):]))

def run(cmd: str, env: dict[str, str] | None) -> str | None:
    'Run given shell command string'
    cmd += ' 2>/dev/null'
    try:
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                             universal_newlines=True, env=env)
    except Exception:
        return None

    if res.returncode != 0:
        return None

    return res.stdout and res.stdout.strip()

def pipe(cmd: list[str], env: dict[str, str] | None) -> Iterator[str]:
    'Run given shell command string and yield output lines'
    res = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                           universal_newlines=True, env=env)
    for line in (res.stdout or []):
        yield line.rstrip()

intercepts = {}
def intercept_cmd(func: Callable) -> None:
    intercepts[func.__name__[4:]] = func

@intercept_cmd
def cmd_list(cmds: list[str], env: dict[str, str] | None) -> bool:
    'Add some extra info to list command output'
    bdir: Path | None = None
    for line in pipe(cmds, env):
        if bdir:
            fields = line.split()
            if len(fields) > 1 and fields[0] == 'package':
                pkg = fields[1]
                jfile = bdir / pkg / 'pipx_metadata.json'
                with jfile.open() as fp:  # type: ignore
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

def cmd_install_common(cmds: list[str], env: dict[str, str] | None) -> bool:
    'Inserts path to pyenv python executable if --python given'
    if any(opt in ('--help', '-h') for opt in cmds):
        # Intercept help output to add enhanced functionality
        for line in pipe(cmds, env):
            if '--python ' in line:
                line = re.sub('--python PYTHON *',
                              '--python PYTHON, -P pyenv_version ', line)
            print(line)
        return True

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
                    cmds[index] = arg + version
                    break
            else:
                continue
        break
    else:
        return False

    # If given python program/version is clearly a path then ignore
    # immediately
    if os.sep in version:
        return False

    # If given python program is a pyenv version then insert the pyenv
    # path to the executable
    pyenv_root = run('pyenv root', env)
    if pyenv_root:
        pyenv_version = run(f'pyenv latest {version}', env)
        if pyenv_version:
            pyexe_path = Path(pyenv_root, 'versions', pyenv_version,
                              'bin', 'python')
            if pyexe_path.exists():
                cmds[index] = arg + str(pyexe_path)

    return False

@intercept_cmd
def cmd_install(cmds: list[str], env: dict[str, str] | None) -> bool:
    return cmd_install_common(cmds, env)

@intercept_cmd
def cmd_reinstall(cmds: list[str], env: dict[str, str] | None) -> bool:
    return cmd_install_common(cmds, env)

@intercept_cmd
def cmd_uninstall(cmds: list[str], env: dict[str, str] | None) -> bool:
    'Intercepts "." arg and substitutes it with package name'
    if '.' not in cmds:
        return False

    pipx_root = run('pipx environment', env)
    if not pipx_root:
        return False

    for line in pipx_root.splitlines():
        if line.startswith('PIPX_HOME='):
            pipx_home_str = line.split('=', 1)[1].strip()
            if pipx_home_str:
                pipx_home = Path(pipx_home_str)
                break
    else:
        return False

    cwd = str(Path.cwd())

    # Iterate over venvs and find one that matches current directory
    for proj in (pipx_home / 'venvs').iterdir():
        mfile = proj / 'pipx_metadata.json'
        if not mfile.exists():
            continue

        mjson = json.loads(mfile.read_text())
        mjson = mjson.get('main_package', {})
        path = mjson.get('package_or_url', '')
        if path.endswith(']'):
            path = path.rsplit('[', 1)[0]

        if path == cwd:
            package = mjson.get('package')
            if package:
                cmds[cmds.index('.')] = package
            break

    return False

def main() -> int | None:
    'Main code'
    # If invoked as root then set appropriate system directories for
    # installs
    env = root_env() if os.geteuid() == 0 else None

    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    cmdlist = ['pipx', cmd] + sys.argv[2:]

    # Intercept any commands we have reimplemented
    cmd = intercepts.get(cmd)
    if cmd and cmd(cmdlist, env):
        return 0

    return subprocess.run(cmdlist, env=env).returncode

if __name__ == '__main__':
    sys.exit(main())
