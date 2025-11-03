#!/usr/bin/env python3
import re
from pathlib import Path

def clean_line(line: str) -> str | None:
    s = line.strip()
    if not s or s.startswith('::') or s.startswith('@echo') or s.startswith('chcp') \
       or s.startswith('cd ') or s.startswith('call ') or s.startswith('set ') \
       or s.startswith('start '):
        return None
    return s.rstrip('^').strip()

def normalize_paths(line: str) -> str:
    # Приведение путей к unix-style
    line = line.replace('%BIN%', '$MODPATH/fake/')
    line = line.replace('%LISTS%\\list-', '$MODPATH/list/list-')
    line = line.replace('%LISTS%\\ipset-', '$MODPATH/ipset/ipset-')
    line = line.replace('\\', '/')
    line = line.replace('"', '')
    line = line.replace('%GameFilter%', '')
    line = re.sub(r',,+', ',', line)
    return line

def normalize_rule(rule: str, index: int) -> str:
    rule = normalize_paths(rule)

    # Исправляем пустые фильтры
    if '--filter-tcp=' in rule:
        rule = re.sub(r'--filter-tcp=,', '--filter-tcp=80,443', rule)
        rule = re.sub(r'--filter-tcp=$', '--filter-tcp=80,443', rule)
    if '--filter-udp=' in rule and index == 8:
        rule = re.sub(r'--filter-udp=$', '--filter-udp=1024-65535', rule)

    rule = re.sub(r'--filter-tcp=80,443,', '--filter-tcp=80,443', rule)
    rule = re.sub(r'\s+', ' ', rule)
    return rule.strip()

def parse_bat_file(bat_file: Path) -> list[str]:
    lines = [clean_line(line) for line in bat_file.read_text(encoding='utf-8', errors='ignore').splitlines()]
    lines = [line for line in lines if line]
    full_text = ' '.join(lines)
    parts = [p.strip() for p in full_text.split('--new') if p.strip()]
    return parts

def write_sh_file(bat_file: Path, out_file: Path):
    parts = parse_bat_file(bat_file)

    with out_file.open('w', encoding='utf-8') as f:
        f.write('#!/bin/bash\n')
        f.write(f'# Zapret Configuration - {bat_file.stem}\n')
        f.write('# Converted from Windows winws.exe config\n\n')

        for i, part in enumerate(parts, start=1):
            rule = normalize_rule(part, i)
            if not rule:
                continue

            comments_map = {
                1: 'UDP 443 для основного списка',
                2: 'UDP 19294-19344,50000-50100 для Discord/STUN',
                3: 'TCP 2053,2083,2087,2096,8443 для Discord media',
                4: 'TCP 443 для Google списка',
                5: 'TCP 80,443 для основного списка',
                6: 'UDP 443 для ipset-all',
                7: 'TCP 80,443 для ipset-all',
                8: 'UDP для ipset-all (catch-all, без GameFilter)',
            }
            comment = f'# Rule {i}: {comments_map.get(i,"")}'
            
            if i == 1:
                f.write(f'{comment}\n')
                f.write(f'config="{rule} --new"\n\n')
            else:
                f.write(f'{comment}\n')
                f.write(f'config="$config {rule} --new"\n\n')

    out_file.chmod(0o755)

def main():
    src_dir = Path('upstream_bats')
    out_dir = Path('module/strategy')
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, bat_file in enumerate(sorted(src_dir.glob('*.bat')), start=1):
        out_file = out_dir / f'flowseal-alt{idx}.sh'
        try:
            write_sh_file(bat_file, out_file)
        except Exception as e:
            print(f"Error processing {bat_file}: {e}")

if __name__ == '__main__':
    main()
