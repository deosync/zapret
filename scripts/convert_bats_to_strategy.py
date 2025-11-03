#!/usr/bin/env python3
import re
from pathlib import Path

def clean_line(line: str) -> str | None:
    """
    Убирает ненужные строки и символы Windows batch
    """
    s = line.strip()
    if not s or s.startswith('::') or s.startswith('@echo') or s.startswith('chcp') \
       or s.startswith('cd ') or s.startswith('call ') or s.startswith('set ') \
       or s.startswith('start '):
        return None
    # убираем символ переноса линии ^
    return s.rstrip('^').strip()

def normalize_rule(rule: str, is_first: bool = False) -> str:
    """
    Преобразует отдельное правило в unix-style конфиг
    """
    rule = rule.strip()
    if not rule:
        return ''
    
    # Заменяем пути Windows на unix-style $MODPATH
    rule = re.sub(r'"%?BIN%\\?', '$MODPATH/fake/', rule, flags=re.IGNORECASE)
    rule = re.sub(r'"%?LISTS%\\?', '$MODPATH/list/', rule, flags=re.IGNORECASE)
    
    # Меняем \ на /
    rule = rule.replace('\\', '/')

    # Убираем winws.exe
    rule = re.sub(r'"[^"]*winws\.exe"\s*', '', rule, flags=re.IGNORECASE)

    # Убираем GameFilter и лишние запятые
    rule = rule.replace('%GameFilter%', '')
    rule = re.sub(r',,+', ',', rule)

    # Убираем все кавычки
    rule = rule.replace('"', '')

    # Исправляем пустые фильтры
    if '--filter-tcp=' in rule:
        rule = re.sub(r'--filter-tcp=,', '--filter-tcp=80,443', rule)
        rule = re.sub(r'--filter-tcp=$', '--filter-tcp=80,443', rule)
    if '--filter-udp=' in rule:
        if rule.endswith('--dpi-desync-cutoff=n3') or rule.strip().endswith('--dpi-desync-any-protocol=1'):
            rule = re.sub(r'--filter-udp=', '--filter-udp=1024-65535', rule)
        else:
            rule = re.sub(r'--filter-udp=$', '--filter-udp=1024-65535', rule)

    # Нормализуем пробелы
    rule = re.sub(r'\s+', ' ', rule)

    return rule.strip()

def main():
    src_dir = Path('upstream_bats')
    out_dir = Path('module/strategy')
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, bat_file in enumerate(sorted(src_dir.glob('*.bat')), start=1):
        try:
            text = bat_file.read_text(encoding='utf-8', errors='ignore')
            lines = [clean_line(line) for line in text.splitlines()]
            lines = [line for line in lines if line]

            full_text = ' '.join(lines)
            parts = [p.strip() for p in full_text.split('--new') if p.strip()]

            out_file = out_dir / f'flowseal-alt{idx}.sh'
            with out_file.open('w', encoding='utf-8') as f:
                f.write('#!/bin/bash\n')
                f.write(f'# Zapret Configuration - {bat_file.stem} (ALT)\n')
                f.write('# Converted from Windows winws.exe config\n\n')

                for i, part in enumerate(parts, start=1):
                    rule = normalize_rule(part, is_first=(i == 1))
                    if not rule:
                        continue

                    # Комментарии к правилам
                    comment = f'# Rule {i}'
                    if i == 1:
                        comment += ': UDP 443 для основного списка'
                    elif i == 2:
                        comment += ': UDP 19294-19344,50000-50100 для Discord/STUN'
                    elif i == 3:
                        comment += ': TCP 2053,2083,2087,2096,8443 для Discord media'
                    elif i == 4:
                        comment += ': TCP 443 для Google списка'
                    elif i == 5:
                        comment += ': TCP 80,443 для основного списка'
                    elif i == 6:
                        comment += ': UDP 443 для ipset-all'
                    elif i == 7:
                        comment += ': TCP 80,443 для ipset-all'
                    elif i == 8:
                        comment += ': UDP для ipset-all (catch-all, без GameFilter)'

                    # Первая строка без $config, последующие добавляются к $config
                    if i == 1:
                        f.write(f'{comment}\n')
                        f.write(f'config="{rule} --new"\n\n')
                    else:
                        f.write(f'{comment}\n')
                        f.write(f'config="$config {rule} --new"\n\n')
            out_file.chmod(0o755)
        except Exception as e:
            print(f"Error processing {bat_file}: {e}")

if __name__ == '__main__':
    main()
