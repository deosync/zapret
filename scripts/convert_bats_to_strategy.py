#!/usr/bin/env python3

import re
import sys
from pathlib import Path

def is_config_file(filename: str) -> bool:
    """Проверяет, является ли файл конфигурационным (начинается с 'general')"""
    return filename.lower().startswith('general')

def extract_winws_command(content: str) -> str:
    """Извлекает команду winws.exe из bat-файла с улучшенным поиском"""
    # Ищем блок с командой winws.exe
    pattern = r'start\s+".*?"\s+/min\s+".*?winws\.exe"\s+(.*)'
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    
    if not match:
        # Попытка найти альтернативный формат
        pattern = r'".*?winws\.exe"\s+(.*)'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    
    if not match:
        raise ValueError("Не удалось найти команду winws.exe в файле")
    
    command = match.group(1)
    # Удаляем символы продолжения строки (^) и объединяем в одну строку
    command = re.sub(r'\^\s*\n\s*', ' ', command)
    command = re.sub(r'\s+', ' ', command).strip()
    
    # Удаляем служебные команды из начала
    command = re.sub(r'^.*?echo:\s*', '', command, flags=re.IGNORECASE)
    
    return command

def cleanup_command(command: str) -> str:
    """Очищает команду от ненужных параметров"""
    # Удаляем параметры wf-tcp и wf-udp, которые не используются в bash
    command = re.sub(r'--wf-tcp=[^ ]* ', '', command)
    command = re.sub(r'--wf-udp=[^ ]* ', '', command)
    return command.strip()

def normalize_paths(line: str) -> str:
    """Приводит пути к unix-стилю и заменяет переменные"""
    # Замена путей для fake-файлов (исправлена ошибка с обрезанием .bin)
    line = re.sub(r'%BIN%\\?([^%"]+\.bin)', r'$MODPATH/fake/\1', line, flags=re.IGNORECASE)
    
    # Замена путей для list-файлов
    line = re.sub(r'%LISTS%\\?list-([^"]+\.txt)', r'$MODPATH/list/list-\1', line, flags=re.IGNORECASE)
    
    # Замена путей для ipset-файлов
    line = re.sub(r'%LISTS%\\?ipset-([^"]+\.txt)', r'$MODPATH/ipset/ipset-\1', line, flags=re.IGNORECASE)
    
    # Удаляем кавычки и нормализуем слеши
    line = line.replace('"', '').replace('\\', '/').replace('//', '/')
    
    # Удаляем %GameFilter% и исправляем запятые
    line = line.replace('%GameFilter%', '')
    line = re.sub(r',,+', ',', line)
    line = re.sub(r'(=),', r'\1', line)
    line = re.sub(r',\s*--', ' --', line)
    line = re.sub(r',\s*$', '', line)
    
    return line.strip()

def normalize_rule(rule: str, index: int, total_rules: int) -> str:
    """Нормализует отдельное правило, исправляя пустые фильтры"""
    rule = normalize_paths(rule)
    
    # Исправляем пустые фильтры TCP/UDP
    rule = re.sub(
        r'(--filter-(?:tcp|udp)=),', 
        r'\180,443,', 
        rule
    )
    
    # Для правила 6 (UDP 443 для ipset-all) - должно быть именно 443
    if index == 6:
        rule = re.sub(
            r'--filter-udp=[^ ]*', 
            '--filter-udp=443',
            rule
        )
    
    # Для последнего правила (UDP catch-all)
    if index == total_rules and "ipset-all.txt" in rule and "--filter-udp=" in rule:
        rule = re.sub(
            r'--filter-udp=[^ ]*', 
            '--filter-udp=1024-65535',
            rule
        )
    
    # Убираем --new из конца правил
    rule = rule.replace('--new', '').strip()
    
    return re.sub(r'\s+', ' ', rule).strip()

def parse_bat_content(content: str) -> list[str]:
    """Парсит содержимое bat-файла и возвращает список правил"""
    command = extract_winws_command(content)
    command = cleanup_command(command)
    
    # Делим на правила по --new
    parts = [p.strip() for p in command.split('--new') if p.strip()]
    return parts

def write_sh_file(bat_file: Path, out_file: Path):
    """Генерирует bash-конфиг из bat-файла"""
    content = bat_file.read_text(encoding='utf-8', errors='ignore')
    rules = parse_bat_content(content)
    total_rules = len(rules)
    
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
            normalized = normalize_rule(rule, i, total_rules)
            if not normalized:
                continue
                
            comment = comments[i-1] if i <= len(comments) else f"Правило {i}"
            f.write(f'# Rule {i}: {comment}\n')
            
            if i == 1:
                # Для первого правила
                if total_rules > 1:
                    f.write(f'config="{normalized} --new"\n\n')
                else:
                    f.write(f'config="{normalized}"\n\n')
            elif i < total_rules:
                f.write(f'config="$config {normalized} --new"\n\n')
            else:
                # Для последнего правила не добавляем --new
                f.write(f'config="$config {normalized}"\n')

    out_file.chmod(0o755)

def main():
    src_dir = Path('upstream_bats')
    out_dir = Path('module/strategy')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    config_files = [f for f in src_dir.glob('*.bat') if is_config_file(f.name)]
    print(f"Найдено конфигурационных файлов: {len(config_files)}")
    
    if not config_files:
        print("ВНИМАНИЕ: Не найдено ни одного конфигурационного файла!")
        print("Конфигурационные файлы должны начинаться с 'general'")
        sys.exit(1)
    
    success_count = 0
    for idx, bat_file in enumerate(sorted(config_files), start=1):
        out_file = out_dir / f'flowseal-alt{idx}.sh'
        try:
            write_sh_file(bat_file, out_file)
            success_count += 1
            print(f"Успешно обработан: {bat_file.name} -> {out_file.name}")
        except Exception as e:
            print(f"ОШИБКА при обработке {bat_file}: {str(e)}")
    
    print(f"\nРезультат: успешно обработано {success_count} из {len(config_files)} файлов")
    if success_count == 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
