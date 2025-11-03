#!/usr/bin/env python3

import re
from pathlib import Path

def extract_winws_command(content: str) -> str:
    """Извлекает команду winws.exe из bat-файла, удаляя префикс start и параметры запуска"""
    # Ищем блок с командой winws.exe с поддержкой многострочных параметров
    pattern = r'start\s+".*?"\s+/min\s+".*?winws\.exe"\s+(.*)'
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError("Не удалось найти команду winws.exe в файле")
    
    command = match.group(1)
    # Удаляем символы продолжения строки (^) и объединяем в одну строку
    command = re.sub(r'\s*\\\s*\n\s*', ' ', command)
    command = re.sub(r'\^\s*\n\s*', ' ', command)
    command = re.sub(r'\s+', ' ', command).strip()
    return command

def normalize_paths(line: str) -> str:
    """Приводит пути к unix-стилю и заменяет переменные"""
    # Замена путей для fake-файлов
    line = re.sub(r'%BIN%([^%]*)\.bin', r'$MODPATH/fake/\1.bin', line, flags=re.IGNORECASE)
    
    # Замена путей для list-файлов
    line = re.sub(r'%LISTS%list-([^"]+\.txt)', r'$MODPATH/list/list-\1', line, flags=re.IGNORECASE)
    
    # Замена путей для ipset-файлов
    line = re.sub(r'%LISTS%ipset-([^"]+\.txt)', r'$MODPATH/ipset/ipset-\1', line, flags=re.IGNORECASE)
    
    # Удаляем кавычки и двойные слеши
    line = line.replace('"', '').replace('\\', '/').replace('//', '/')
    
    # Удаляем %GameFilter% и исправляем запятые
    line = line.replace('%GameFilter%', '')
    line = re.sub(r',,+', ',', line)
    return line.strip()

def normalize_rule(rule: str, index: int) -> str:
    """Нормализует отдельное правило, исправляя пустые фильтры"""
    rule = normalize_paths(rule)
    
    # Исправляем пустые фильтры TCP
    rule = re.sub(
        r'(--filter-tcp=)(?:,|$)', 
        r'\180,443', 
        rule
    )
    
    # Для последнего правила (UDP catch-all)
    if index == 8:
        rule = re.sub(
            r'--filter-udp=,?', 
            '--filter-udp=1024-65535 ', 
            rule
        )
    
    # Удаляем дублирующиеся параметры
    rule = re.sub(r'(--new\s*)+', '--new ', rule)
    return re.sub(r'\s+', ' ', rule).strip()

def parse_bat_content(content: str) -> list[str]:
    """Парсит содержимое bat-файла и возвращает список правил"""
    command = extract_winws_command(content)
    # Разделяем на правила по --new, сохраняя порядок
    parts = []
    current_rule = []
    for token in command.split():
        if token == '--new' and current_rule:
            parts.append(' '.join(current_rule))
            current_rule = []
        else:
            current_rule.append(token)
    if current_rule:
        parts.append(' '.join(current_rule))
    return [p.strip() for p in parts if p.strip()]

def write_sh_file(bat_file: Path, out_file: Path):
    """Генерирует bash-конфиг из bat-файла"""
    content = bat_file.read_text(encoding='utf-8', errors='ignore')
    rules = parse_bat_content(content)
    
    comments = [
        "UDP 443 для основного списка",
        "UDP 19294-19344,50000-50100 для Discord/STUN",
        "TCP 2053,2083,2087,2096,8443 для Discord media",
        "TCP 443 для Google списка",
        "TCP 80,443 для основного списка",
        "UDP 443 для ipset-all",
        "TCP 80,443 для ipset-all",
        "UDP для ipset-all (catch-all, без GameFilter)",
    ]
    
    with out_file.open('w', encoding='utf-8') as f:
        f.write('#!/bin/bash\n')
        f.write(f'# Zapret Configuration - {bat_file.stem}\n')
        f.write('# Converted from Windows winws.exe config\n\n')
        
        for i, rule in enumerate(rules, 1):
            normalized = normalize_rule(rule, i)
            if not normalized:
                continue
                
            comment = comments[i-1] if i <= len(comments) else f"Rule {i}"
            f.write(f'# Rule {i}: {comment}\n')
            
            if i == 1:
                f.write(f'config="{normalized} --new"\n\n')
            else:
                f.write(f'config="$config {normalized} --new"\n\n')
    
    out_file.chmod(0o755)

def main():
    src_dir = Path('upstream_bats')
    out_dir = Path('module/strategy')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for idx, bat_file in enumerate(sorted(src_dir.glob('*.bat')), start=1):
        out_file = out_dir / f'flowseal-alt{idx}.sh'
        try:
            write_sh_file(bat_file, out_file)
            print(f"Успешно обработан: {bat_file.name} -> {out_file.name}")
        except Exception as e:
            print(f"Ошибка при обработке {bat_file}: {str(e)}")

if __name__ == '__main__':
    main()
