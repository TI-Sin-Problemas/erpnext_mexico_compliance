"""Functions to run on app installation"""
from . import setup


def after_install():
    """Runs after install of app"""
    setup.install_big_fixtures()
