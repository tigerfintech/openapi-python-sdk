# -*- coding: utf-8 -*-
"""
Tests for CLI main group, version command, and global options.
"""
import unittest
from click.testing import CliRunner


class TestMainGroup(unittest.TestCase):
    """Tests for the root 'tigeropen' CLI group."""

    def setUp(self):
        self.runner = CliRunner()

    def test_main_group_exists(self):
        """The tigeropen CLI entry point should be importable and callable."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)

    def test_main_group_shows_help(self):
        """tigeropen --help should show help text with available commands."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Usage', result.output)

    def test_version_command(self):
        """tigeropen version should print the SDK version."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['version'])
        self.assertEqual(result.exit_code, 0)
        # Should contain a version string like '3.5.5'
        self.assertRegex(result.output.strip(), r'\d+\.\d+\.\d+')

    def test_global_format_option(self):
        """tigeropen --format json should accept format option."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['--format', 'json', 'version'])
        self.assertEqual(result.exit_code, 0)

    def test_global_format_invalid_choice(self):
        """tigeropen --format xml should fail with invalid choice."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['--format', 'xml', 'version'])
        self.assertNotEqual(result.exit_code, 0)

    def test_global_verbose_option(self):
        """tigeropen -v version should accept verbose flag."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['-v', 'version'])
        self.assertEqual(result.exit_code, 0)

    def test_subcommand_groups_registered(self):
        """config, quote, trade, account, push subgroups should be registered."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['--help'])
        for cmd in ['config', 'quote', 'trade', 'account', 'push', 'version']:
            self.assertIn(cmd, result.output, f"'{cmd}' command not found in help output")


if __name__ == '__main__':
    unittest.main()
