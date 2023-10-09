## PIPXX - Wrapper for pipx to add some minor functionality
[![PyPi](https://img.shields.io/pypi/v/pipxx)](https://pypi.org/project/pipxx/)

[`pipxx`][pipxx] is a simple command line utility to wrap the usage of
[`pipx`][pipx] to provide some minor improved functions. Consider
[`pipxx`][pipxx] a proof of concept of some ideas for [`pipx`][pipx].

1. [Global application installation by
   root](#enhancement-1-global-application-installation-by-root).
2. [Enhancement of pipx list
   output](#enhancement-2-improved-pipx-list-output).
3. [Automatic determination of pyenv Python path for
   install](#enhancement-3-automatic-determination-of-pyenv-python-path-for-install).
4. [Substitution of current directory with package name for
   uninstall](#enhancement-4-substitution-of-current-directory-with-package-name-for-uninstall).

See the description of these enhancements below.

`pipxx` is merely a wrapper for `pipx` so takes exactly the same command
line arguments and options. Just run `pipxx` the same as you would run
`pipx`. Type `pipx` or `pipx -h` to view the usage summary for `pipx`
(or type `pipxx` or `pipxx -h` to see the same usage summary).

The latest version and documentation is available at
https://github.com/bulletmark/pipxx.

### Enhancement 1: Global application installation by root

`pipx` is used normally to install applications for a single user. It
can also [install applications
globally](https://pypa.github.io/pipx/installation/#installation-options)
as root but that is [awkward](https://github.com/pypa/pipx/issues/754)
because you have to manually set environment variables. `pipxx`
recognises when it is run as root (or with `sudo`) and automatically
sets appropriate system global `PIPX_BIN_DIR` and `PIPX_HOME`
directories for `pipx`.

E.g. to install application as normal user:

```bash
$ pipxx install cowsay
```

To install application for all users (i.e. globally):

```bash
$ sudo pipxx install cowsay
```

Note, to see the global directories selected by `pipxx` for your system:

```bash
$ sudo pipxx environment
   ```

### Enhancement 2: Improved pipx list output

[`pipx list`](https://pypa.github.io/pipx/docs/#pipx-list)
output lacks some useful information. `pipxx` adds the following
to the `pipx list` output:

1. The PyPi package name, or source directory, or VCS URL from where the
   application was installed from,
2. Whether the application is installed as
   [__editable__](https://pypa.github.io/pipx/docs/#pipx-install).

### Enhancement 3: Automatic determination of pyenv Python path for install

When installing, you can tell `pipx` to use a specific version/path of
Python using the `--python` option. Unfortunately, you have to specify
the full path to the python interpreter you want. Very commonly, users
use [`pyenv`](https://github.com/pyenv/pyenv) to install install
multiple versions of Python.

So with `pipx` you have to type:

```sh
$ pipx install --python ~/.pyenv/versions/3.12.0/bin/python cowsay
```

With `pipxx` you merely have to type:

```sh
$ pipxx install --python 3.12 cowsay
```

I.e. `pipxx` will work out from `3.12` that you want the path
`~/.pyenv/versions/3.12.0/bin/python`, i.e. the latest `3.12` version
installed at the time of this example. You could alternately type `pipxx
install --python 3 cowsay`, or `pipxx install --python 3.12.0 cowsay`.

Note the automatically selected path is dependent on your
system/installation and is derived by `pipxx` from the output of `pyenv
root`.

Actually, `--python` is a commonly used option but unfortunately `pipx`
does not provide a short-form option for it. So `pipxx` also adds `-P`
as an alias for `--python` allowing you to simply type:

```sh
$ pipxx install -P 3.12 cowsay
```

Note that `pipxx` also adds a description of the added pyenv version
option and the added `-P` alias option to the `install --help` output.

### Enhancement 4: Substitution of current directory with package name for uninstall

Developers often use `pipx` to install and run an application they are
working on from a local source directory. E.g. for an example
application `myapp`:

```sh
$ pwd
/home/myname/src/myapp
$ pipx install -e .
installed package myapp <...>
```

To uninstall this application you have to type `pipx uninstall myapp`.
However, thinking symmetrically, you would expect `pipx uninstall .`
would suffice. So `pipxx` adds the ability to do this:


```sh
$ pipxx uninstall .
uninstalled myapp!
```

## Installation or upgrade or removal

Note [pipxx is on PyPI](https://pypi.org/project/pipxx/) so just ensure
that [`pipx`](https://pypa.github.io/pipx/) is installed then type the
following:

To install:

```bash
$ pipx install pipxx
```

To upgrade:

```bash
$ pipx upgrade pipxx
```

To remove:

```bash
$ pipx uninstall pipxx
```

`pipxx` requires Python >= 3.7 and requires no 3rd party packages. It
requires that `pipx` is in your `$PATH`.

## License

Copyright (C) 2023 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License.
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later
version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License at <http://www.gnu.org/licenses/> for more details.

[pipxx]: https://github.com/bulletmark/pipxx
[pipx]: https://pypa.github.io/pipx/

<!-- vim: se ai syn=markdown: -->
