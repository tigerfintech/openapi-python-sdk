# -*- coding: utf-8 -*-
"""
Tests for the CLI 'skills' command: list and read embedded agent-readable skills.
"""
import unittest
from click.testing import CliRunner

import pytest


# 纯单测：skills 命令只读包内文件，不碰真实接口
pytestmark = pytest.mark.unit


class TestSkillsList(unittest.TestCase):
    """Tests for 'tigeropen skills list'."""

    def setUp(self):
        self.runner = CliRunner()

    def test_skills_list_shows_all_skills(self):
        """skills list should show the five built-in skills."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['skills', 'list'])
        self.assertEqual(result.exit_code, 0, result.output)
        for name in ('tigeropen-shared', 'tigeropen-cli', 'tigeropen-quote',
                     'tigeropen-trade', 'tigeropen-push'):
            self.assertIn(name, result.output)

    def test_skills_list_json(self):
        """skills list --json should return a parseable JSON envelope."""
        import json
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['skills', 'list', '--json'])
        self.assertEqual(result.exit_code, 0, result.output)
        data = json.loads(result.output)
        self.assertTrue(data['ok'])
        names = {s['name'] for s in data['skills']}
        self.assertEqual(names, {'tigeropen-shared', 'tigeropen-cli', 'tigeropen-quote',
                                 'tigeropen-trade', 'tigeropen-push'})


class TestSkillsRead(unittest.TestCase):
    """Tests for 'tigeropen skills read'."""

    def setUp(self):
        self.runner = CliRunner()

    def test_read_skill_markdown(self):
        """skills read <name> should print the SKILL.md frontmatter."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['skills', 'read', 'tigeropen-shared'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn('name: tigeropen-shared', result.output)

    def test_read_reference_slash_form(self):
        """skills read <name>/references/<file>.md should print that file."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['skills', 'read', 'tigeropen-cli/references/oauth2.md'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn('OAuth2', result.output)

    def test_read_unknown_skill_fails(self):
        """skills read <unknown> should fail with a non-zero exit."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['skills', 'read', 'tigeropen-unknown'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('unknown skill', result.output)


if __name__ == '__main__':
    unittest.main()
