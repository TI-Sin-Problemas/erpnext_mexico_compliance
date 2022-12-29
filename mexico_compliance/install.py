"""Installation tasks"""
from .setup import split_big_fixtures, remove_splitted_fixtures


def after_sync():
    """Run tasks after migration sync"""
    remove_splitted_fixtures()


def before_install():
    """Run tasks before installation"""
    split_big_fixtures()
