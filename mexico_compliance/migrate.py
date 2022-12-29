"""Migration tasks"""
from .setup import split_big_fixtures, remove_splitted_fixtures


def after_migrate():
    """Run after migration taskis"""
    remove_splitted_fixtures()


def before_migrate():
    """Run after migration tasks"""
    split_big_fixtures()
