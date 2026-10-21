# Command-Line Interface (CLI) Usage

After installing `propakai`, a few commands become available in your terminal. This page documents
their usage.


## `propakai-info`

Displays package information like the version number, the package's directory and the path to the
ITU data files.

### Usage & Example

```console
$ propakai-info
propakai version: 1.2.3
Package location: /home/user/venv/lib/python3.12/site-packages/propakai
ITU data files location: /home/user/.local/share/propakai/itu_proprietary
```


## `propakai-data-cleanup`

Deletes all installed ITU digital maps and other ITU data files. 

Downloaded ITU digital maps and data files are not automatically removed when PropaKai is
uninstalled, as they are not part of the installation process. This command provides an easy way to
delete them before uninstalling. When PropaKai is installed within multiple Python installations
or virtual environments for a same user, they all share the same ITU maps and data files to avoid
storing them multiple times.

You may also use this command simply to free up disk space while continuing to use PropaKai.
PropaKai is able to download the ITU files again whenever they are required for a calculation.

### Usage

```bash
propakai-data-cleanup [-y | --yes]
```

### Options

| Option        | Short | Description                                  | Default |
|---------------|-------|----------------------------------------------|---------|
| `--yes`       | `-y`  | Proceed without asking for confirmation      | `False` |

### Example

```console
$ propakai-data-cleanup
Will delete 200 file(s) (1306.3 MB) from:
  C:\Users\user\AppData\Local\propakai\propakai\itu_proprietary
Proceed (Y/n)? y
200 file(s) deleted (1306.3 MB).
```


## `propakai-bin-cleanup`

Deletes pre-compiled binaries that are unsuitable for the current operating system and processor
architecture.

PropaKai ships with a few binaries for different systems (Windows, Linux, macOS) and architectures
(x86_64, arm64). While these files are small, you can use this command to remove the ones not
needed by your current system.

Unlike the ITU data files, all packaged binary files are automatically and completely removed when
you uninstall propakai.


### Usage

```bash
propakai-bin-cleanup [-y | --yes]
```

### Options

| Option        | Short | Description                                  | Default |
|---------------|-------|----------------------------------------------|---------|
| `--yes`       | `-y`  | Proceed without asking for confirmation      | `False` |


### Example

```console
$ propakai-bin-cleanup
Will delete:
  /home/user/venv/lib/python3.12/site-packages/propakai/bin/win
  /home/user/venv/lib/python3.12/site-packages/propakai/bin/macos
  /home/user/venv/lib/python3.12/site-packages/propakai/bin/linux/arm64
Proceed (Y/n)? y
Deleted directory "/home/user/venv/lib/python3.12/site-packages/propakai/bin/win"
Deleted directory "/home/user/venv/lib/python3.12/site-packages/propakai/bin/macos"
Deleted directory "/home/user/venv/lib/python3.12/site-packages/propakai/bin/linux/arm64"
```