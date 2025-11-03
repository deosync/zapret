#!/usr/bin/env python3

import re
import sys
from pathlib import Path

def extract_winws_command(content: str) -> str:
    """Извлекает команду winws.exe из bat-файла с улучшенным поиском"""
    # Попытка 1: поиск классического формата с start
    pattern1 = r'start\s+".*?"\s+/min\s+".*?winws\.exe"\s+(.*)'
    match = re.search(pattern1, content, re.IGNORECASE | re.DOTALL)
    
    if match:
        return cleanup_command(match.group(1))
    
    # Попытка 2: поиск прямого вызова winws.exe
    pattern2 = r'".*?winws\.exe"\s+(.*)'
    match = re.search(pattern2, content, re.IGNORECASE | re.DOTALL)
    
    if match:
        return cleanup_command(match.group(1))
    
    # Попытка 3: поиск любой строки содержащей winws.exe
    for line in content.splitlines():
        if 'winws.exe' in line.lower():
            # Извлекаем часть после winws.exe
            parts = line.split('winws.exe', 1)
            if len(parts) > 1:
                cleaned = cleanup_command(parts[1])
                if cleaned:
                    return cleaned
    
    raise ValueError("Не удалось найти команду winws.exe в файле. Проверьте формат исходного файла.")

def cleanup_command(command: str) -> str:
    """Очищает команду от артефактов BAT-файла"""
    # Удаляем символы продолжения строки (^) и объединяем в одну строку
    command = re.sub(r'\^\s*\n\s*', ' ', command)
    command = re.sub(r'\s+', ' ', command)
    # Удаляем префиксы и постфиксы, которые не являются частью команды
    command = command.split('echo:', 1)[-1]
    command = re.sub(r'^\s*"', '', command)
    command = re.sub(r'"\s*$', '', command)
    command = re.sub(r'^\s*:', '', command)  # Удаляем начальные двоеточия
    return command.strip()

def normalize_paths(line: str) -> str:
    """Приводит пути к unix-стилю и заменяет переменные"""
    # Замена путей для fake-файлов
    line = re.sub(r'%BIN%\\([^%"]+\.bin)', r'$MODPATH/fake/\g<1>', line, flags=re.IGNORECASE)
    line = re.sub(r'%BIN%([^%"]+\.bin)', r'$MODPATH/fake/\g<1>', line, flags=re.IGNORECASE)
    
    # Замена путей для list-файлов
    line = re.sub(r'%LISTS%\\list-([^"]+\.txt)', r'$MODPATH/list/list-\g<1>', line, flags=re.IGNORECASE)
    line = re.sub(r'%LISTS%list-([^"]+\.txt)', r'$MODPATH/list/list-\g<1>', line, flags=re.IGNORECASE)
    
    # Замена путей для ipset-файлов
    line = re.sub(r'%LISTS%\\ipset-([^"]+\.txt)', r'$MODPATH/ipset/ipset-\g<1>', line, flags=re.IGNORECASE)
    line = re.sub(r'%LISTS%ipset-([^"]+\.txt)', r'$MODPATH/ipset/ipset-\g<1>', line, flags=re.IGNORECASE)
    
    # Удаляем кавычки и нормализуем слеши
    line = line.replace('"', '').replace('\\', '/').replace('//', '/')
    
    # Удаляем %GameFilter% и исправляем запятые
    line = line.replace('%GameFilter%', '')
    line = re.sub(r',,+', ',', line)
    return line.strip()

def normalize_rule(rule: str, index: int) -> str:
    """Нормализует отдельное правило, исправляя пустые фильтры"""
    rule = normalize_paths(rule)
    
    # Исправляем пустые фильтры TCP/UDP с использованием \g<1> вместо \1
    rule = re.sub(
        r'(--filter-(?:tcp|udp)=)(?:,|$)', 
        r'\g<1>80,443', 
        rule
    )
    
    # Для последнего правила (UDP catch-all)
    if "ipset-all.txt" in rule and "--filter-udp=" in rule and "--filter-udp=1024-65535" not in rule:
        rule = re.sub(
            r'--filter-udp=(?:[^ ]*)', 
            '--filter-udp=1024-65535', 
            rule
        )
    
    return re.sub(r'\s+', ' ', rule).strip()

def parse_bat_content(content: str) -> list[str]:
    """Парсит содержимое bat-файла и возвращает список правил"""
    command = extract_winws_command(content)
    print(f"Найдена команда: {command[:100]}...")  # Отладка
    
    # Делим на правила по --new, но сохраняем --new в результатах
    parts = []
    current = []
    tokens = command.split()
    
    for token in tokens:
        current.append(token)
        if token == "--new":
            parts.append(" ".join(current))
            current = []
    
    if current:  # Добавляем последнее правило, даже если нет --new в конце
        parts.append(" ".join(current))
    
    parts = [p.strip().replace("--new", "").strip() for p in parts if p.strip()]
    print(f"Найдено правил: {len(parts)}")  # Отладка
    return parts

def write_sh_file(bat_file: Path, out_file: Path):
    """Генерирует bash-конфиг из bat-файла"""
    print(f"Обработка файла: {bat_file}")
    
    if not bat_file.exists():
        raise FileNotFoundError(f"Исходный файл не найден: {bat_file}")
    
    content = bat_file.read_text(encoding='utf-8', errors='ignore')
    if not content.strip():
        raise ValueError(f"Исходный файл пустой: {bat_file}")
    
    print(f"Размер содержимого: {len(content)} байт")
    
    rules = parse_bat_content(content)
    
    # Заготовки комментариев для правил
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
        
        written_rules = 0
        for i, rule in enumerate(rules, 1):
            if not rule.strip():
                continue
                
            normalized = normalize_rule(rule, i)
            if not normalized:
                print(f"Правило {i} стало пустым после нормализации")
                continue
                
            comment = comments[i-1] if i <= len(comments) else f"Правило {i}"
            f.write(f'# Rule {i}: {comment}\n')
            
            if written_rules == 0:
                f.write(f'config="{normalized} --new"\n\n')
            else:
                f.write(f'config="$config {normalized} --new"\n\n')
            written_rules += 1
        
        if written_rules == 0:
            print(f"ВНИМАНИЕ: Ни одно правило не было записано в {out_file.name}")
            f.write('# WARNING: No rules were converted. Check the source file format.\n')
    
    out_file.chmod(0o755)
    print(f"Создан файл: {out_file} с {written_rules} правилами")

def main():
    src_dir = Path('upstream_bats')
    out_dir = Path('module/strategy')
    
    print(f"Поиск BAT-файлов в: {src_dir.absolute()}")
    if not src_dir.exists():
        print(f"Директория {src_dir} не существует. Создание...")
        src_dir.mkdir(parents=True, exist_ok=True)
    
    bat_files = list(src_dir.glob('*.bat'))
    print(f"Найдено BAT-файлов: {len(bat_files)}")
    
    if not bat_files:
        print("ВНИМАНИЕ: Не найдено ни одного BAT-файла для конвертации!")
        print("Поместите исходные BAT-файлы в директорию upstream_bats/")
        sys.exit(1)
    
    out_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    for idx, bat_file in enumerate(sorted(bat_files), start=1):
        # Пропускаем service.bat, так как это не конфигурация winws
        if bat_file.name.lower() == "service.bat":
            print(f"Пропуск служебного файла: {bat_file.name}")
            continue
            
        out_file = out_dir / f'flowseal-alt{idx}.sh'
        try:
            write_sh_file(bat_file, out_file)
            success_count += 1
        except Exception as e:
            print(f"ОШИБКА при обработке {bat_file}: {str(e)}")
            # Создаем файл с сообщением об ошибке
            with out_file.open('w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'# ERROR converting {bat_file.name}: {str(e)}\n')
                f.write('# Please check the source file format\n')
            out_file.chmod(0o755)
    
    print(f"\nРезультат: успешно обработано {success_count} из {len(bat_files)} файлов")
    if success_count == 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
