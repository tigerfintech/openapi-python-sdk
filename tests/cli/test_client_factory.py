# -*- coding: utf-8 -*-
"""
Tests for CLI client factory and private key resolution.
"""
import os
import unittest
import tempfile
import shutil


class TestResolvePrivateKey(unittest.TestCase):
    """Tests for private key resolution: file path, string content, env var."""

    def test_resolve_private_key_from_file_path(self):
        """Should read private key content when given a valid file path."""
        from tigeropen.cli.client_factory import resolve_private_key
        temp_dir = tempfile.mkdtemp()
        try:
            key_file = os.path.join(temp_dir, 'private_key.pem')
            with open(key_file, 'w') as f:
                f.write('-----BEGIN RSA PRIVATE KEY-----\nMIIBogIBAAJBATestKey\n-----END RSA PRIVATE KEY-----')
            result = resolve_private_key(key_file)
            self.assertEqual(result, 'MIIBogIBAAJBATestKey')
        finally:
            shutil.rmtree(temp_dir)

    def test_resolve_private_key_from_string(self):
        """Should return the string directly when not a file path."""
        from tigeropen.cli.client_factory import resolve_private_key
        key_str = 'MIIBogIBAAJBADirectKeyString'
        result = resolve_private_key(key_str)
        self.assertEqual(result, key_str)

    def test_resolve_private_key_from_pem_string(self):
        """Should strip PEM headers when given a full PEM string."""
        from tigeropen.cli.client_factory import resolve_private_key
        pem = '-----BEGIN RSA PRIVATE KEY-----\nMIIBogIBAAJBAInlineKey\n-----END RSA PRIVATE KEY-----'
        result = resolve_private_key(pem)
        self.assertEqual(result, 'MIIBogIBAAJBAInlineKey')

    def test_resolve_private_key_empty_returns_empty(self):
        """Should return empty string for empty input."""
        from tigeropen.cli.client_factory import resolve_private_key
        result = resolve_private_key('')
        self.assertEqual(result, '')

    def test_resolve_private_key_none_returns_empty(self):
        """Should return empty string for None input."""
        from tigeropen.cli.client_factory import resolve_private_key
        result = resolve_private_key(None)
        self.assertEqual(result, '')


class TestBuildConfig(unittest.TestCase):
    """Tests for building TigerOpenClientConfig from CLI context."""

    def test_build_config_from_ctx_obj(self):
        """Should create a config with values from context dict."""
        from tigeropen.cli.client_factory import build_config
        ctx_obj = {
            'config_path': None,
            'tiger_id': 'test_id',
            'account': 'test_account',
            'private_key': 'test_key',
        }
        config = build_config(ctx_obj)
        self.assertEqual(config.tiger_id, 'test_id')
        self.assertEqual(config.account, 'test_account')
        self.assertEqual(config.private_key, 'test_key')

    def test_build_config_from_props_path(self):
        """Should load config from properties file when config_path is given."""
        from tigeropen.cli.client_factory import build_config
        temp_dir = tempfile.mkdtemp()
        try:
            props_file = os.path.join(temp_dir, 'tiger_openapi_config.properties')
            with open(props_file, 'w') as f:
                f.write('tiger_id=props_id\n')
                f.write('account=props_account\n')
                f.write('private_key_pk8=props_key\n')
            ctx_obj = {'config_path': temp_dir}
            config = build_config(ctx_obj)
            self.assertEqual(config.tiger_id, 'props_id')
            self.assertEqual(config.account, 'props_account')
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
