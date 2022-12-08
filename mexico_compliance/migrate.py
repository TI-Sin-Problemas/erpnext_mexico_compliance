"""Migration setup functions"""

from . import setup


def after_migrate():
    """Run after migrate tasks"""
    setup.install_big_fixtures()
