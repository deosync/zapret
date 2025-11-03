#!/usr/bin/env python3
import re
from pathlib import Path

def clean_line(line):
    s = line.strip()
    if not s or s.startswith('::') or s.startswith('@echo') or s.startswith('chcp') or \
       s.startswith('cd ') or s.startswith('call ') or s.startswith('set ') or s.startswith('start '):
        return None
    return s.rstrip('^').strip()

def normalize_rule(rule):
    rule = re.sub(r'\s+', ' ', rule)
    rule = re.sub(r'--([a-z\-]+)\s+', r'--\1=', rule)
    rule = rule.replace('"', '')
    rule = rule.replace('\\', '/')
    rule = re.sub(r'%BIN%|"[^"]*\\bin\\', '$MODPATH/fake/', rule)
    rule = re.sub(r'%LISTS%|"[^"]*\\lists\\', '$MODPATH/list/', rule)
    rule = re.sub(r'%GameFilter%', '', rule)
    rule = re.sub(r'"[^"]*winws\.exe"\s*', '', rule)
    rule = re.sub(r'--wf-tcp[=\s]+[0-9,\-]+\s*', '', rule)
    rule = re.sub(r'--wf-udp[=\s]+[0-9,\-]+\s*', '', rule)
    return rule.strip()

def main():
    src = Path('upstream_bats')
    out_dir = Path('module/strategy')
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, bat in enumerate(sorted(src.glob('*.bat')), start=1):
        try:
            text = bat.read_text(encoding='utf-8', errors='ignore')
            lines = [clean_line(l) for l in text.splitlines()]
            lines = [l for l in lines if l]
            full = ' '.join(lines)

            # Разделяем по --new
            parts = [p.strip() for p in full.split('--new') if p.strip()]

            out_file = out_dir / f'flowseal-alt{idx}.sh'
            with out_file.open('w', encoding='utf-8') as f:
                f.write(f'#!/bin/bash\n')
                f.write(f'# Zapret Configuration - {bat.stem}\n')
                f.write(f'# Converted from Windows winws.exe config\n\n')

                for i, p in enumerate(parts, start=1):
                    rule = normalize_rule(p)
                    if not rule:
                        continue
                    comment = f'# Rule {i}'
                    if i == 1:
                        f.write(f'{comment}: UDP 443 для основного списка\n')
                        f.write(f'config="{rule} --new"\n\n')
                    else:
                        # Автоматически добавляем к config
                        # Исправляем пустые фильтры
                        rule = rule.replace('--filter-tcp=,', '--filter-tcp=80,443')
                        if '--filter-udp=' in rule and rule.endswith('='):
                            rule = rule.replace('--filter-udp=', '--filter-udp=1024-65535')
                        f.write(f'{comment}: правило {i}\n')
                        f.write(f'config="$config {rule} --new"\n\n')
            out_file.chmod(0o755)
        except Exception as e:
            print(f"Error processing {bat}: {e}")

if __name__ == '__main__':
    main()
