# -*- coding: utf-8 -*-
"""
Output formatting module for CLI.
Supports table, json, csv formats.
"""
import csv
import io
import json
import sys

import pandas as pd


def is_empty(data):
    """Check if data is empty (None, empty DataFrame, empty list, etc.)."""
    if data is None:
        return True
    if isinstance(data, pd.DataFrame):
        return data.empty
    if isinstance(data, (list, dict)):
        return len(data) == 0
    return False


def to_records(items):
    """Convert a list of domain objects to a list of dicts for rendering.
    If items is already a DataFrame, return it as-is.
    Handles objects with __dict__, __slots__ + to_dict(), or plain dicts."""
    if isinstance(items, pd.DataFrame):
        return items
    records = []
    for item in items:
        if hasattr(item, 'to_dict'):
            d = item.to_dict()
        elif hasattr(item, '__dict__'):
            d = item.__dict__
        else:
            records.append(item)
            continue
        # Flatten nested objects to str for display
        flat = {}
        for k, v in d.items():
            if v is not None and hasattr(v, '__dict__') and not isinstance(v, (str, int, float, bool)):
                flat[k] = str(v)
            elif isinstance(v, list) and v and hasattr(v[0], '__dict__'):
                flat[k] = str(v)
            else:
                flat[k] = v
        records.append(flat)
    return records


def render(data, fmt='table', file=None):
    """
    Render data in the specified format.

    :param data: DataFrame, dict, list of dicts, string, or None
    :param fmt: 'table', 'json', or 'csv'
    :param file: output file object, defaults to sys.stdout
    """
    if file is None:
        file = sys.stdout

    if data is None:
        return

    if isinstance(data, str):
        file.write(data + '\n')
        return

    if fmt == 'json':
        _render_json(data, file)
    elif fmt == 'csv':
        _render_csv(data, file)
    else:
        _render_table(data, file)


def _render_table(data, file):
    if isinstance(data, pd.DataFrame):
        if data.empty:
            return
        file.write(data.to_string(index=False) + '\n')
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        df = pd.DataFrame(data)
        file.write(df.to_string(index=False) + '\n')
    elif isinstance(data, dict):
        for k, v in data.items():
            file.write(f'{k}: {v}\n')
    else:
        file.write(str(data) + '\n')


def _render_json(data, file):
    if isinstance(data, pd.DataFrame):
        records = data.to_dict(orient='records')
        file.write(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    elif isinstance(data, (dict, list)):
        file.write(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n')
    else:
        file.write(json.dumps(str(data), ensure_ascii=False) + '\n')


def _render_csv(data, file):
    if isinstance(data, pd.DataFrame):
        if data.empty:
            return
        file.write(data.to_csv(index=False))
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    elif isinstance(data, dict):
        writer = csv.writer(file)
        writer.writerow(['key', 'value'])
        for k, v in data.items():
            writer.writerow([k, v])
