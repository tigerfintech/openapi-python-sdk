# -*- coding: utf-8 -*-
"""Keeps the CLI tests off the developer's own machine state.

Choosing an authentication mode reads the token store, so without this a developer who has
authorized locally resolves differently from CI.
"""
import tempfile

import pytest


@pytest.fixture(autouse=True)
def isolated_tigeropen_home(monkeypatch):
    """Point the token store at an empty directory. A test that wants a stored
    authorization creates one under it."""
    with tempfile.TemporaryDirectory(prefix='tigeropen-cli-home-') as home:
        monkeypatch.setenv('TIGEROPEN_HOME', home)
        yield home
