## PIPXX - Wrapper for pipx to add some minor functionality
[`pipxx`][pipxx] is a simple command line utility to wrap the usage of
[`pipx`][pipx] to provide a couple of improved functions:

1. [Global application installation by root](#global-application-installation-by-root)
2. [Enhancement of pipx list output](#enhancement-of-pipx-list-output)

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

## Installation or upgrade or removal

Ensure that [`pipx`](https://pypa.github.io/pipx/) is installed then type:

To install:

```bash
$ pipx install git+https://github.com/bulletmark/pipxx
```

To upgrade:

```bash
$ pipx install -f git+https://github.com/bulletmark/pipxx
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
