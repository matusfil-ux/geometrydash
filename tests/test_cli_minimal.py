#
# Copyright © 2020 Merck Sharp & Dohme Corp., a subsidiary of Merck & Co., Inc.
# All rights reserved.
#
"""
Validate that __main__ calls cli.
"""

import sys

import pytest

from msd_dags_geometrydash import __version__
from msd_dags_geometrydash.cli import cli as cli_function


try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


def test_cli_from_main_help(mocker, capsys):
    """Should call working cli()."""
    main_args = sys.argv[0:1] + ["--help"]
    mocker.patch.object(sys, "argv", main_args)
    with pytest.raises(SystemExit) as exc:
        from msd_dags_geometrydash.__main__ import main

        main()
    ic(exc.value)
    assert exc.value.args[0] == 0
    out, err = capsys.readouterr()
    if cli_function.__doc__ is not None:
        first_line_from_docstring = cli_function.__doc__.strip().split("\n")[0]
        assert (first_line_from_docstring in out) or (first_line_from_docstring in err)


def test_cli_from_main_version(mocker, capsys):
    """Should call version cli()."""
    main_args = sys.argv[0:1] + ["--version"]
    mocker.patch.object(sys, "argv", main_args)
    with pytest.raises(SystemExit) as exc:
        from msd_dags_geometrydash.__main__ import main

        main()
    ic(exc.value)
    assert exc.value.args[0] == 0
    out, err = capsys.readouterr()
    assert (__version__ == out.strip()) or (__version__ == err.strip())


def test_cli_from_main_empty(mocker):
    """Should call empty cli()."""
    main_args = sys.argv[0:1]
    mocker.patch.object(sys, "argv", main_args)
    with pytest.raises(SystemExit) as exc:
        from msd_dags_geometrydash.__main__ import main

        main()
    ic(exc.value)
    assert exc.value.args[0] == 0


def test_cli_from_main_wrong(mocker, capsys):
    """Should call wrong cli()."""
    main_args = sys.argv[0:1] + ["--non-existent-option-that-really-does-not-exist-at-all-like-for-real-and-stuff"]
    mocker.patch.object(sys, "argv", main_args)
    with pytest.raises(SystemExit) as exc:
        from msd_dags_geometrydash.__main__ import main

        main()
    ic(exc.value)
    assert exc.value.args[0] == 2  # noqa: PLR2004
    _, err = capsys.readouterr()
    assert "No such option" in err
