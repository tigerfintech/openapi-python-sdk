# -*- coding: utf-8 -*-
"""
Tests for CLI config commands: init, show, set, path.
"""
import os
import unittest
import tempfile
import shutil
from click.testing import CliRunner


class TestConfigInit(unittest.TestCase):
    """Tests for 'tigeropen config init' interactive setup."""

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_init_creates_properties_file(self):
        """config init should create tiger_openapi_config.properties via interactive prompts."""
        from tigeropen.cli.main import cli
        # Prompts: tiger_id, account, private_key (+ blank line), secret_key(skip), config_dir
        result = self.runner.invoke(cli, ['config', 'init'],
                                    input=f'test_id\ntest_account\ntest_private_key_content\n\n\n{self.temp_dir}\n')
        self.assertEqual(result.exit_code, 0)
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        self.assertTrue(os.path.exists(props_file))

    def test_config_init_writes_correct_values(self):
        """config init should write tiger_id, account, private_key to properties file."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['config', 'init'],
                                    input=f'my_tiger_id\nmy_account\nmy_private_key\n\n\n{self.temp_dir}\n')
        self.assertEqual(result.exit_code, 0)
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        content = open(props_file, 'r').read()
        self.assertIn('my_tiger_id', content)
        self.assertIn('my_account', content)
        self.assertIn('my_private_key', content)


class TestConfigShow(unittest.TestCase):
    """Tests for 'tigeropen config show'."""

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        # Create a minimal properties file
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        with open(props_file, 'w') as f:
            f.write('tiger_id=show_test_id\n')
            f.write('account=show_test_account\n')
            f.write('private_key_pk8=ABCDEF1234567890SECRETKEY\n')

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_show_displays_config(self):
        """config show should display current configuration."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['-c', self.temp_dir, 'config', 'show'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('show_test_id', result.output)
        self.assertIn('show_test_account', result.output)

    def test_config_show_masks_private_key(self):
        """config show should mask the private key content."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['-c', self.temp_dir, 'config', 'show'])
        self.assertEqual(result.exit_code, 0)
        # Should NOT show the full key
        self.assertNotIn('ABCDEF1234567890SECRETKEY', result.output)


class TestConfigSet(unittest.TestCase):
    """Tests for 'tigeropen config set'."""

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        with open(props_file, 'w') as f:
            f.write('tiger_id=old_id\n')
            f.write('account=old_account\n')

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_set_updates_value(self):
        """config set tiger_id new_id should update the value in properties file."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['-c', self.temp_dir, 'config', 'set', 'tiger_id', 'new_id'])
        self.assertEqual(result.exit_code, 0)
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        content = open(props_file, 'r').read()
        self.assertIn('new_id', content)


class TestConfigPath(unittest.TestCase):
    """Tests for 'tigeropen config path'."""

    def setUp(self):
        self.runner = CliRunner()

    def test_config_path_shows_path(self):
        """config path should print the config directory path."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['config', 'path'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(len(result.output.strip()) > 0)

    def test_config_path_with_custom_path(self):
        """config path with -c should show the custom path."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['-c', '/tmp/custom_config', 'config', 'path'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('/tmp/custom_config', result.output)


class TestConfigShowMissing(unittest.TestCase):
    """Tests for config show when config file doesn't exist."""

    def setUp(self):
        self.runner = CliRunner()

    def test_config_show_missing_file(self):
        """config show should report missing config file gracefully."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['-c', '/tmp/nonexistent_dir_12345', 'config', 'show'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('not found', result.output)


class TestConfigInitWithPemKey(unittest.TestCase):
    """Tests for config init with PEM-formatted private key."""

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_init_strips_pem_headers(self):
        """config init with PEM key should strip BEGIN/END headers."""
        from tigeropen.cli.main import cli
        pem_key = '-----BEGIN RSA PRIVATE KEY-----ABCDEF123456-----END RSA PRIVATE KEY-----'
        result = self.runner.invoke(cli, ['config', 'init'],
                                    input=f'test_id\ntest_account\n{pem_key}\n\n\n{self.temp_dir}\n')
        self.assertEqual(result.exit_code, 0)
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        content = open(props_file, 'r').read()
        self.assertNotIn('-----BEGIN', content)
        self.assertIn('ABCDEF123456', content)

    def test_config_init_with_file_path_key(self):
        """config init with a file path should read key from file."""
        from tigeropen.cli.main import cli
        # Create a temp key file
        key_file = os.path.join(self.temp_dir, 'private.pem')
        with open(key_file, 'w') as f:
            f.write('-----BEGIN RSA PRIVATE KEY-----\nFILEKEYCONTENT123\n-----END RSA PRIVATE KEY-----\n')

        config_dir = os.path.join(self.temp_dir, 'config')
        result = self.runner.invoke(cli, ['config', 'init'],
                                    input=f'test_id\ntest_account\n{key_file}\n\n\n{config_dir}\n')
        self.assertEqual(result.exit_code, 0)
        props_file = os.path.join(config_dir, 'tiger_openapi_config.properties')
        self.assertTrue(os.path.exists(props_file))

    def test_config_init_with_multiline_key(self):
        """config init should join multi-line pasted private key into one string."""
        from tigeropen.cli.main import cli
        # Simulate pasting a multi-line key: 3 lines + blank line to finish
        result = self.runner.invoke(cli, ['config', 'init'],
                                    input=f'test_id\ntest_account\nAAAA\nBBBB\nCCCC\n\n\n{self.temp_dir}\n')
        self.assertEqual(result.exit_code, 0)
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        content = open(props_file, 'r').read()
        self.assertIn('AAAABBBBCCCC', content)


class TestConfigSetNew(unittest.TestCase):
    """Tests for config set creating new properties."""

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_set_adds_new_key(self):
        """config set should add a new key to an existing config."""
        from tigeropen.cli.main import cli
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        with open(props_file, 'w') as f:
            f.write('tiger_id=existing_id\n')

        result = self.runner.invoke(cli, ['-c', self.temp_dir, 'config', 'set', 'license', 'TBUS'])
        self.assertEqual(result.exit_code, 0)
        content = open(props_file, 'r').read()
        self.assertIn('TBUS', content)
        self.assertIn('existing_id', content)


class TestConfigEnvVar(unittest.TestCase):
    """Tests for TIGEROPEN_PROPS_PATH env var."""

    def setUp(self):
        self.runner = CliRunner()

    def test_config_path_from_env_var(self):
        """config path should use TIGEROPEN_PROPS_PATH env var when no -c flag."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['config', 'path'],
                                    env={'TIGEROPEN_PROPS_PATH': '/tmp/env_config_dir'})
        self.assertEqual(result.exit_code, 0)
        self.assertIn('/tmp/env_config_dir', result.output)


class TestConfigShowFilePath(unittest.TestCase):
    """Tests for config show with direct file path (not directory)."""

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_show_with_file_path(self):
        """config show -c /path/to/file.properties should read the file directly."""
        from tigeropen.cli.main import cli
        props_file = os.path.join(self.temp_dir, 'custom.properties')
        with open(props_file, 'w') as f:
            f.write('tiger_id=file_path_id\naccount=file_path_account\n')

        result = self.runner.invoke(cli, ['-c', props_file, 'config', 'show'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('file_path_id', result.output)

    def test_config_set_with_file_path(self):
        """config set -c /path/to/file.properties should write to the file directly."""
        from tigeropen.cli.main import cli
        props_file = os.path.join(self.temp_dir, 'custom.properties')
        with open(props_file, 'w') as f:
            f.write('tiger_id=old_val\n')

        result = self.runner.invoke(cli, ['-c', props_file, 'config', 'set', 'tiger_id', 'new_val'])
        self.assertEqual(result.exit_code, 0)
        content = open(props_file, 'r').read()
        self.assertIn('new_val', content)


class TestConfigInitFullOptions(unittest.TestCase):
    """Tests for config init with all optional fields."""

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_init_with_secret(self):
        """config init with secret_key should write it to properties."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['config', 'init'],
                                    input=f'test_id\ntest_account\ntest_key\n\nmy_secret\n{self.temp_dir}\n')
        self.assertEqual(result.exit_code, 0)
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        content = open(props_file, 'r').read()
        self.assertIn('my_secret', content)


if __name__ == '__main__':
    unittest.main()
