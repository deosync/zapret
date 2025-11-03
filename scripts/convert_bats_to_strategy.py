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
    # Убираем все вызовы winws.exe и echo
    rule = re.sub(r'^(echo:)?\s*', '', rule)
    rule = re.sub(r'"[^"]*winws\.exe"\s*', '', rule)
    rule = re.sub(r'start\s+"[^"]*"\s*/min\s*', '', rule)
    
    # Заменяем переменные путей
    rule = rule.replace('%BIN%', '$MODPATH/fake/')
    rule = rule.replace('%LISTS%', '$MODPATH/list/')

    # ipset файлы
    rule = re.sub(r'\$MODPATH/list/ipset-(\S+\.txt)', r'$MODPATH/ipset/ipset-\1', rule)

    # Преобразуем пустые фильтры
    rule = re.sub(r'--filter-(tcp|udp)=,', r'--filter-\1=80,443', rule)
    rule = re.sub(r'--filter-(tcp|udp)=$', lambda m: '--filter-udp=1024-65535' if m.group(1) == 'udp' else '--filter-tcp=80,443', rule)

    # Убираем wf-* параметры
    rule = re.sub(r'--wf-tcp[=\s]+[0-9,\-]*\s*', '', rule)
    rule = re.sub(r'--wf-udp[=\s]+[0-9,\-]*[0-9,\-]*\s*', '', rule)

    # Убираем GameFilter, если он остался
    rule = rule.replace('%GameFilter%', '')

    # Убираем лишние пробелы
    rule = re.sub(r'\s+', ' ', rule)
    return rule.strip()

def generate_rule_comment(rule, idx):
    # Простейшая генерация читаемого комментария
    if '--filter-udp=' in rule:
        return f'# Rule {idx}: UDP {re.search(r"--filter-udp=([0-9,\-]+)", rule).group(1) if re.search(r"--filter-udp=([0-9,\-]+)", rule) else ""}'
    if '--filter-tcp=' in rule:
        return f'# Rule {idx}: TCP {re.search(r"--filter-tcp=([0-9,\-]+)", rule).group(1) if re.search(r"--filter-tcp=([0-9,\-]+)", rule) else ""}'
    return f'# Rule {idx}'

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
                f.write('#!/bin/bash\n')
                f.write(f'# Zapret Configuration - {bat.stem}\n')
                f.write('# Converted from Windows winws.exe config\n\n')

                for i, p in enumerate(parts, start=1):
                    rule = normalize_rule(p)
                    if not rule:
                        continue
                    comment = generate_rule_comment(rule, i)
                    if i == 1:
                        f.write(f'{comment} для основного списка\n')
                        f.write(f'config="{rule} --new"\n\n')
                    else:
                        f.write(f'{comment}\n')
                        f.write(f'config="$config {rule} --new"\n\n')
            out_file.chmod(0o755)
        except Exception as e:
            print(f"Error processing {bat}: {e}")

if __name__ == '__main__':
    main()
