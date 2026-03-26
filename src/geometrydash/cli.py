#
# Copyright © 2025 Merck Sharp & Dohme Corp., a subsidiary of Merck & Co., Inc.
# All rights reserved.
#
"""
Entrypoint for all Command Line Interface.
"""

import click

from . import __version__


@click.command()
@click.version_option(version=__version__, message="%(version)s")
def cli() -> None:  # noqa
    """Command Line Interface for Geometry DASH.

    TODO: Write this yourself.
    Use this as a starting CLI point for your python package.

    """
    pass
