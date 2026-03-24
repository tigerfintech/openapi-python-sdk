# -*- coding: utf-8 -*-
"""
Tests for CLI output formatting module.
"""
import io
import json
import unittest
import pandas as pd


class TestRenderTable(unittest.TestCase):
    """Tests for table format rendering."""

    def test_render_dataframe_as_table(self):
        """render() with format='table' should produce readable table from DataFrame."""
        from tigeropen.cli.formatting import render
        df = pd.DataFrame({'symbol': ['AAPL', 'GOOG'], 'price': [150.0, 2800.0]})
        output = io.StringIO()
        render(df, fmt='table', file=output)
        text = output.getvalue()
        self.assertIn('AAPL', text)
        self.assertIn('GOOG', text)
        self.assertIn('150', text)

    def test_render_dict_list_as_table(self):
        """render() should handle a list of dicts as table."""
        from tigeropen.cli.formatting import render
        data = [{'symbol': 'AAPL', 'status': 'open'}, {'symbol': 'GOOG', 'status': 'open'}]
        output = io.StringIO()
        render(data, fmt='table', file=output)
        text = output.getvalue()
        self.assertIn('AAPL', text)
        self.assertIn('GOOG', text)

    def test_render_single_dict_as_table(self):
        """render() should handle a single dict as key-value table."""
        from tigeropen.cli.formatting import render
        data = {'tiger_id': 'test123', 'account': 'DU123456'}
        output = io.StringIO()
        render(data, fmt='table', file=output)
        text = output.getvalue()
        self.assertIn('test123', text)
        self.assertIn('DU123456', text)


class TestRenderJson(unittest.TestCase):
    """Tests for JSON format rendering."""

    def test_render_dataframe_as_json(self):
        """render() with format='json' should produce valid JSON from DataFrame."""
        from tigeropen.cli.formatting import render
        df = pd.DataFrame({'symbol': ['AAPL'], 'price': [150.0]})
        output = io.StringIO()
        render(df, fmt='json', file=output)
        parsed = json.loads(output.getvalue())
        self.assertIsInstance(parsed, list)
        self.assertEqual(parsed[0]['symbol'], 'AAPL')

    def test_render_dict_as_json(self):
        """render() with format='json' should produce valid JSON from dict."""
        from tigeropen.cli.formatting import render
        data = {'key': 'value', 'number': 42}
        output = io.StringIO()
        render(data, fmt='json', file=output)
        parsed = json.loads(output.getvalue())
        self.assertEqual(parsed['key'], 'value')

    def test_render_dict_list_as_json(self):
        """render() with format='json' should produce valid JSON from list of dicts."""
        from tigeropen.cli.formatting import render
        data = [{'a': 1}, {'a': 2}]
        output = io.StringIO()
        render(data, fmt='json', file=output)
        parsed = json.loads(output.getvalue())
        self.assertEqual(len(parsed), 2)


class TestRenderCsv(unittest.TestCase):
    """Tests for CSV format rendering."""

    def test_render_dataframe_as_csv(self):
        """render() with format='csv' should produce CSV from DataFrame."""
        from tigeropen.cli.formatting import render
        df = pd.DataFrame({'symbol': ['AAPL', 'GOOG'], 'price': [150.0, 2800.0]})
        output = io.StringIO()
        render(df, fmt='csv', file=output)
        text = output.getvalue()
        self.assertIn('symbol', text)
        self.assertIn('AAPL', text)
        # CSV should contain commas
        self.assertIn(',', text)

    def test_render_dict_list_as_csv(self):
        """render() with format='csv' should produce CSV from list of dicts."""
        from tigeropen.cli.formatting import render
        data = [{'symbol': 'AAPL', 'price': 150}, {'symbol': 'GOOG', 'price': 2800}]
        output = io.StringIO()
        render(data, fmt='csv', file=output)
        text = output.getvalue()
        self.assertIn('symbol', text)
        self.assertIn('AAPL', text)


class TestRenderEmpty(unittest.TestCase):
    """Tests for edge cases."""

    def test_render_empty_dataframe(self):
        """render() should handle empty DataFrame without error."""
        from tigeropen.cli.formatting import render
        df = pd.DataFrame()
        output = io.StringIO()
        render(df, fmt='table', file=output)
        # Should not raise

    def test_render_none(self):
        """render() should handle None data gracefully."""
        from tigeropen.cli.formatting import render
        output = io.StringIO()
        render(None, fmt='table', file=output)
        # Should not raise

    def test_render_string(self):
        """render() should handle plain string data."""
        from tigeropen.cli.formatting import render
        output = io.StringIO()
        render('hello world', fmt='table', file=output)
        self.assertIn('hello world', output.getvalue())

    def test_render_empty_list(self):
        """render() should handle empty list without error."""
        from tigeropen.cli.formatting import render
        output = io.StringIO()
        render([], fmt='table', file=output)
        # Should output '[]' as string, not crash
        self.assertIn('[]', output.getvalue())

    def test_render_empty_dict(self):
        """render() should handle empty dict without error."""
        from tigeropen.cli.formatting import render
        output = io.StringIO()
        render({}, fmt='table', file=output)
        # Should not crash

    def test_render_empty_dataframe_csv(self):
        """render() csv with empty DataFrame should not crash."""
        from tigeropen.cli.formatting import render
        df = pd.DataFrame()
        output = io.StringIO()
        render(df, fmt='csv', file=output)
        # Should not raise

    def test_render_empty_dataframe_json(self):
        """render() json with empty DataFrame should produce valid JSON."""
        from tigeropen.cli.formatting import render
        df = pd.DataFrame()
        output = io.StringIO()
        render(df, fmt='json', file=output)
        parsed = json.loads(output.getvalue())
        self.assertEqual(parsed, [])


class TestToRecords(unittest.TestCase):
    """Tests for to_records helper."""

    def test_to_records_with_dict_objects(self):
        """to_records() should extract __dict__ from objects."""
        from tigeropen.cli.formatting import to_records

        class MockObj:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        items = [MockObj(a=1, b=2), MockObj(a=3, b=4)]
        records = to_records(items)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['a'], 1)
        self.assertEqual(records[1]['b'], 4)

    def test_to_records_with_plain_dicts(self):
        """to_records() should pass through plain dicts."""
        from tigeropen.cli.formatting import to_records
        items = [{'x': 1}, {'x': 2}]
        records = to_records(items)
        self.assertEqual(records, [{'x': 1}, {'x': 2}])


class TestIsEmpty(unittest.TestCase):
    """Tests for is_empty helper."""

    def test_is_empty_none(self):
        from tigeropen.cli.formatting import is_empty
        self.assertTrue(is_empty(None))

    def test_is_empty_empty_dataframe(self):
        from tigeropen.cli.formatting import is_empty
        self.assertTrue(is_empty(pd.DataFrame()))

    def test_is_empty_empty_list(self):
        from tigeropen.cli.formatting import is_empty
        self.assertTrue(is_empty([]))

    def test_is_empty_empty_dict(self):
        from tigeropen.cli.formatting import is_empty
        self.assertTrue(is_empty({}))

    def test_is_empty_nonempty_dataframe(self):
        from tigeropen.cli.formatting import is_empty
        self.assertFalse(is_empty(pd.DataFrame({'a': [1]})))

    def test_is_empty_nonempty_list(self):
        from tigeropen.cli.formatting import is_empty
        self.assertFalse(is_empty([1, 2]))

    def test_is_empty_string(self):
        from tigeropen.cli.formatting import is_empty
        self.assertFalse(is_empty('hello'))


if __name__ == '__main__':
    unittest.main()
