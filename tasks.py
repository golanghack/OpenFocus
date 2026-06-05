import os
import sys

import invoke

use_pty = sys.platform != "win32" and sys.stdout.isatty()


@invoke.task
def check_linters(ctx):
    ctx.run("pip check", echo=True, pty=use_pty)
    ctx.run("poetry check", echo=True, pty=use_pty)

    result_black = ctx.run(
        "black --check --diff --color .", echo=True, pty=use_pty, warn=True
    )
    result_mypy = ctx.run("mypy .", echo=True, pty=use_pty, warn=True)
    result_ruff = ctx.run("ruff check .", echo=True, pty=use_pty, warn=True)

    if not (result_ruff.ok and result_mypy.ok and result_black.ok):
        raise invoke.Exit(message="Check failed!")


@invoke.task(aliases=["format"])
def formatters(ctx):
    ctx.run("black .", echo=True)
    ctx.run("ruff check . --fix", echo=True)


@invoke.task
def tests(ctx, migrations=False, fail_on_dead_fixtures=False):
    os.environ["ENV"] = "TESTING"
    ctx.run(
        "pytest --dead-fixtures --dup-fixtures",
        echo=True,
        warn=not fail_on_dead_fixtures,
    )
    ctx.run("pytest -x", echo=True, pty=use_pty)
