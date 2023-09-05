#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MyApp CLI interface

This API provides a similar experience as the CLI, but in Python.

Example:
``` py title="test.py"
from myapp.cli import cli_app

myapp = cli_app()
myapp.info()
myapp.apply()
```

This is a quite complete CLI template for your App, you will probably want
to remove 80% of this file.


Author: MrJK
License: GPLv3
"""

import logging
import os
import sys
import traceback
from enum import Enum
from pathlib import Path
from pprint import pprint
from typing import Optional

import json
from ruamel import yaml
import typer

# import sh
# import pyaml
# from loguru import logger

from wrt_backup.app import MyApp
from wrt_backup.errors import MyAppException

# Base Application example
# ===============================

logging.basicConfig()
logger = logging.getLogger('wrt_backup')
# logger = logging.getLogger(name="myapp.cli")
__version__ = "0.1.0"




class OutputFormat(str, Enum):
    "Available output formats"

    # pylint: disable=invalid-name
    python = "python"
    yaml = "yaml"
    json = "json"
    toml = "toml"


def render_output(ret, fmt=OutputFormat.yaml):
    if fmt == OutputFormat.yaml:
        print (yaml.dump(ret, default_flow_style=False))
    elif fmt == OutputFormat.python:
        pprint (ret)
    elif fmt == OutputFormat.json:
        print (json.dumps(ret, indent=2))
    else:
        assert False, f"Unsuppored fmt: {fmt}"


# Core application definition
# ===============================

# Define Typer application
# -------------------
cli_app = typer.Typer(
    help="MyApp, that does something",
    invoke_without_command=True,
    no_args_is_help=True,
)


# Define an init function, with common options
# -------------------
@cli_app.callback()
def main(
    ctx: typer.Context,
    verbose: int = typer.Option(0, "--verbose", "-v", count=True, min=0, max=2),
    working_dir: Optional[str] = typer.Option(
        # ".",  # For relative paths
        #os.getcwd(),  # For abolute Paths
        "",
        "-c",
        "--config",
        help="Path of myapp.yml configuration file or directory.",
        envvar="MYAPP_PROJECT_DIR",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version",
    ),
):
    """
    MyApp Command Line Interface.
    """

    # Set logging level
    # -------------------
    # 50: Crit
    # 40: Err
    # 30: Warn
    # 20: Info
    # 10: Debug
    # 0: Not set
    verbose = 30 - (verbose * 10)
    verbose = verbose if verbose > 10 else logging.DEBUG
    logger.setLevel(level=verbose)

    # Init myapp
    # -------------------
    if version:
        print(__version__)
        return

    ctx.obj = {
        "myapp": MyApp(path=working_dir),
    }


# Simple commands example
# ===============================


@cli_app.command("help")
def cli_help(
    ctx: typer.Context,
):
    """Show this help message"""
    print(ctx.parent.get_help())

@cli_app.command("backup")
def cli_backup(
    ctx: typer.Context,
    list_files: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List files only",
    ),
    ):
    """Backup router config"""

    # Test logging:
    # -------------------
    app = ctx.obj['myapp']

    app.cmd_backup(list_files=list_files)


@cli_app.command("show")
def cli_show(
    ctx: typer.Context,
    fmt: OutputFormat = typer.Option(
        OutputFormat.yaml.value,
        "--format",
        "-F",
        help="Output format",
    ),
    limit: str = typer.Option(
        None,
        "--limit",
        "-L",
        help="List of hosts to select",
    ),
    structured: bool = typer.Option(
        True,
        "--structured",
        "-S",
        help="Enable structured format",
    ),
    native_type: bool = typer.Option(
        True,
        "--native",
        "-N",
        help="Use lists instead of dict when possible",
    ),
    ):
    """Show uci export"""

    app = ctx.obj['myapp']
    ret = app.cmd_uci_show(native_type=native_type, structured=structured, limit=limit)
    render_output(ret, fmt=fmt)


@cli_app.command("fw_show")
def cli_fw_show(
    ctx: typer.Context,
    fmt: OutputFormat = typer.Option(
        OutputFormat.yaml.value,
        "--format",
        "-F",
        help="Output format",
    ),
    limit: str = typer.Option(
        None,
        "--limit",
        "-L",
        help="List of hosts to select",
    ),
    ):
    """Show firmware info"""

    app = ctx.obj['myapp']
    ret = app.cmd_fw_show(limit=limit)
    render_output(ret, fmt=fmt)

@cli_app.command("fw_download")
def cli_fw_download(
    ctx: typer.Context,
    fmt: OutputFormat = typer.Option(
        OutputFormat.yaml.value,
        "--format",
        "-F",
        help="Output format",
    ),
    limit: str = typer.Option(
        None,
        "--limit",
        "-L",
        help="List of hosts to select",
    ),
    release: str = typer.Option(
        None,
        "--release",
        "-r",
        help="Openwrt release to select",
    ),
    ):
    """Show firmware info"""

    app = ctx.obj['myapp']
    ret = app.cmd_fw_download(limit=limit, version=release)
    render_output(ret, fmt=fmt)



@cli_app.command("hosts")
def cli_hosts(
    ctx: typer.Context,
    fmt: OutputFormat = typer.Option(
        OutputFormat.yaml.value,
        "--format",
        "-F",
        help="Output format",
    ),
    ):
    """Show host inventory"""
    app = ctx.obj['myapp']
    render_output(app.cmd_inventory(), fmt=fmt)



#@cli_app.command("logging")
#def cli_logging(
#    ctx: typer.Context,
#):
#    """Test logging"""
#
#    # Test logging:
#    # -------------------
#    logger.critical("SHOW CRITICAL")
#    logger.error("SHOW ERROR")
#    logger.warning("SHOW WARNING")
#    logger.info("SHOW INFO")
#
#
## pylint: disable=redefined-builtin
#@cli_app.command("command1")
#def cli_command1(
#    ctx: typer.Context,
#    mode: Optional[str] = typer.Option(
#        "Default Mode",
#        help="Write anything here",
#    ),
#    format: OutputFormat = typer.Option(
#        OutputFormat.yaml.value,
#        help="Output format",
#    ),
#    target: Optional[str] = typer.Argument(
#        None,
#        help="Target directory or all",
#    ),
#):
#    """Command1 example"""
#    myapp = ctx.obj["myapp"]
#
#    print(
#        f"Run {myapp} with '{target}' as target in mode '{mode}' in format '{format}'"
#    )
#    print("This is a dump of our cli context:")
#    pprint(ctx.__dict__)
#
#    print("Run MyApp")
#    myapp.hello()
#    myapp.world()
#
#
## Source Command SubGroup Example
## ===============================
#cli_src = typer.Typer(help="Manage sources")
#cli_app.add_typer(cli_src, name="group1")
#
#
#@cli_src.callback()
#def src_callback():
#    """
#    Manage sources in the app.
#    """
#    print("Executed before all source commands")
#
#
#@cli_src.command("ls")
#def src_ls():
#    """List sources"""
#    print("List sources")
#
#
#@cli_src.command("install")
#def src_install():
#    """Install sources"""
#    print("Install a source")
#
#
#@cli_src.command("update")
#def src_update():
#    """Update sources"""
#    print("Update sources")


# Exception handler
# ===============================
def clean_terminate(err):
    "Terminate nicely the program depending the exception"

    oserrors = [
        PermissionError,
        FileExistsError,
        FileNotFoundError,
        InterruptedError,
        IsADirectoryError,
        NotADirectoryError,
        TimeoutError,
    ]

    # Choose dead end way
    if isinstance(err, MyAppException):
        err_name = err.__class__.__name__
        advice = getattr(err, 'advice', None)
        if advice:
            logger.warning(err.advice)

        logger.error(err)
        logger.critical("MyApp exited with: error %s: %s", err.rc, err_name)
        sys.exit(err.rc)

    # Examples:

    # if isinstance(err, yaml.parser.ParserError):
    #     logger.critical(err)
    #     logger.critical("MyApp exited with: YAML Parser error (file format)")
    #     sys.exit(error.YAMLError.rc)

    # if isinstance(err, sh.ErrorReturnCode):
    #     logger.critical(err)
    #     logger.critical(
    #         "MyApp exited with: failed command returned %s", err.exit_code)
    #     sys.exit(error.ShellCommandFailed.rc)

    if err.__class__ in oserrors:
        # Decode OS errors
        # errno = os.strerror(err.errno)
        # errint = str(err.errno)

        logger.critical("MyApp exited with OS error: %s", err)
        sys.exit(err.errno)


# Core application definition
# ===============================


def app():
    "Return a MyApp App instance"

    try:
        return cli_app()

    # pylint: disable=broad-except
    except Exception as err:
        clean_terminate(err)

        # Developper catchall
        logger.error(traceback.format_exc())
        logger.critical("Uncatched error %s; this may be a bug!", err.__class__)
        logger.critical("Exit 1 with bugs")
        sys.exit(1)


if __name__ == "__main__":
    app()

