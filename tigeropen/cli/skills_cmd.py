# -*- coding: utf-8 -*-
"""
Skills command: list and read the agent-readable skill content shipped with the CLI.

The skill files live under ``tigeropen/cli/skills/`` (packaged with the wheel), so
``skills`` works from any working directory and always matches the installed CLI
version. Inspired by lark-cli's ``skills`` subcommand: each domain has its own
SKILL.md, plus references/ files for deeper detail.
"""
import re
import sys
from pathlib import Path

import click

_SKILLS_ROOT = Path(__file__).resolve().parent / 'skills'

_FRONTMATTER = re.compile(r'\A---\n(.*?)\n---\n', re.DOTALL)


def _iter_skills():
    """Yield (name, skill_dir) for every skill directory under skills/."""
    if not _SKILLS_ROOT.is_dir():
        return
    for entry in sorted(_SKILLS_ROOT.iterdir()):
        if entry.is_dir() and (entry / 'SKILL.md').is_file():
            yield entry.name, entry


def _read_skill_file(skill_dir, rel_path):
    """Read a file under a skill dir, or None if it does not exist or escapes."""
    target = (skill_dir / rel_path).resolve()
    root = skill_dir.resolve()
    if not str(target).startswith(str(root)):
        return None
    if not target.is_file():
        return None
    return target.read_text(encoding='utf-8')


def _parse_frontmatter(text):
    """Return the frontmatter as a dict, or {} when absent.

    Handles flat ``key: value`` pairs and YAML block scalars (``key: >`` /
    ``key: |`` followed by indented lines, folded with spaces).
    """
    m = _FRONTMATTER.match(text)
    if not m:
        return {}
    data = {}
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ':' not in line:
            i += 1
            continue
        key, _, raw = line.partition(':')
        key = key.strip()
        value = raw.strip().strip('"\'')
        # Block scalar continuation: collect subsequent indented lines.
        if value in ('>', '|'):
            parts = []
            i += 1
            while i < len(lines) and lines[i].startswith((' ', '\t')):
                parts.append(lines[i].strip())
                i += 1
            data[key] = ' '.join(parts)
            continue
        data[key] = value
        i += 1
    return data


@click.group('skills')
def skills():
    """Read agent-readable skill content embedded in the CLI."""
    pass


@skills.command('list')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON envelope.')
def skills_list(as_json):
    """List the skills shipped with this CLI."""
    result = []
    for name, skill_dir in _iter_skills():
        text = _read_skill_file(skill_dir, 'SKILL.md') or ''
        meta = _parse_frontmatter(text)
        result.append({
            'name': name,
            'description': meta.get('description', ''),
            'version': meta.get('version', ''),
            'cliHelp': meta.get('cliHelp', ''),
        })

    if as_json:
        import json
        click.echo(json.dumps({'ok': True, 'skills': result}, ensure_ascii=False, indent=2))
        return
    if not result:
        click.echo('No skills found.')
        return
    for item in result:
        click.echo('%s%s' % (item['name'], (' — %s' % item['description']) if item['description'] else ''))
        if item['cliHelp']:
            click.echo('    %s' % item['cliHelp'])


@skills.command('read')
@click.argument('path')
@click.argument('subpath', required=False)
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON envelope.')
def skills_read(path, subpath, as_json):
    """Print a skill's SKILL.md, or a file under the skill.

    PATH is ``<name>`` for the SKILL.md, or ``<name>/<relative-path>``.
    ``tigeropen skills read <name> <relative-path>`` (space form) also works.
    """
    name = path.split('/')[0]
    rel_path = path.partition('/')[2] or subpath or 'SKILL.md'

    for skill_name, skill_dir in _iter_skills():
        if skill_name == name:
            content = _read_skill_file(skill_dir, rel_path)
            if content is None:
                click.echo('Error: %s not found under skill %s' % (rel_path, name), err=True)
                sys.exit(1)
            if as_json:
                import json
                click.echo(json.dumps({'ok': True, 'name': name, 'path': rel_path, 'content': content},
                                      ensure_ascii=False))
            else:
                click.echo(content, nl=False)
            return

    click.echo('Error: unknown skill %s' % name, err=True)
    click.echo('Run "tigeropen skills list" to see available skills.')
    sys.exit(1)
