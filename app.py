#!/usr/bin/env python3
"""
Минималистичный счетчик дней с настраиваемой подписью и цветом фона
Поддерживает несколько счетчиков на отдельных страницах
"""

from flask import Flask, render_template, request, send_from_directory
from datetime import datetime, date
import argparse
import sys
import os
import re

app = Flask(__name__)

# Словарь для хранения счетчиков: {имя_страницы: {параметры}}
COUNTERS = {}

def parse_date(date_str):
    """Парсит дату из строки"""
    try:
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y.%m.%d'):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Неверный формат даты: {date_str}")
    except Exception as e:
        print(f"Ошибка парсинга даты: {e}")
        sys.exit(1)

def parse_color(color_str):
    """Парсит цвет из строки и возвращает также читаемое имя"""
    if not color_str:
        return '#667eea-#764ba2', 'Синий'
    
    color_str = color_str.strip().lower()
    
    # Предопределенные градиенты с русскими названиями
    gradients = {
        'blue': ('#667eea-#764ba2', 'Синий'),
        'green': ('#11998e-#38ef7d', 'Зеленый'),
        'orange': ('#f46b45-#eea849', 'Оранжевый'),
        'purple': ('#8a2be2-#da70d6', 'Фиолетовый'),
        'red': ('#ff416c-#ff4b2b', 'Красный'),
        'sunset': ('#ff7e5f-#feb47b', 'Закат'),
        'ocean': ('#2193b0-#6dd5ed', 'Океан'),
        'forest': ('#56ab2f-#a8e063', 'Лес'),
        'berry': ('#8e2de2-#4a00e0', 'Ягодный'),
    }
    
    # Если это предопределенный градиент
    if color_str in gradients:
        return gradients[color_str]
    
    # Если это hex цвета (например, #667eea-#764ba2)
    if '-' in color_str:
        parts = color_str.split('-')
        if len(parts) == 2:
            hex_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
            if hex_pattern.match(parts[0].strip()) and hex_pattern.match(parts[1].strip()):
                return color_str, 'Пользовательский'
    
    # Если это одиночный hex цвет, создаем градиент
    hex_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    if hex_pattern.match(color_str):
        # Создаем градиент из одного цвета
        return f'{color_str}-{color_str}', 'Пользовательский'
    
    # По умолчанию синий градиент
    return gradients['blue']

@app.route('/favicon.ico')
def favicon():
    """Обработка favicon"""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    """Главная страница - список доступных счетчиков"""
    
    # Подготавливаем данные для шаблона (только для счетчиков, созданных через --counter)
    counters_data = {}
    for page_name, counter in COUNTERS.items():
        counters_data[page_name] = {
            'date': counter['date'],
            'label': counter['label'],
            'color': counter['color'],
            'color_name': counter.get('color_name', 'Пользовательский')
        }
    
    context = {
        'counters': counters_data,
        'current_time': datetime.now().strftime('%H:%M:%S %d.%m.%Y')
    }
    
    # Рендерим шаблон списка счетчиков
    return render_template('counters_list.html', **context)

@app.route('/<page_name>')
def counter_page(page_name):
    """Обработчик для отдельных страниц счетчиков"""
    # Получаем параметры из URL
    url_date = request.args.get('date')
    url_label = request.args.get('label')
    url_color = request.args.get('color')
    
    # Проверяем, существует ли предустановленный счетчик
    if page_name in COUNTERS:
        # Используем предустановленный счетчик
        counter_data = COUNTERS[page_name]
        target_date = counter_data['date']
        label = counter_data['label']
        color_hex = counter_data['color']
    else:
        # Если счетчик не предустановлен, проверяем наличие параметров в URL
        if not url_date:
            # Если нет параметров в URL, возвращаем ошибку
            return f"""
            <h1>Счетчик '{page_name}' не найден</h1>
            <p>Этот счетчик не настроен как постоянный.</p>
            <p>Используйте параметры URL для создания временного счетчика:</p>
            <p><code>?date=ГГГГ-ММ-ДД&label=Надпись&color=цвет</code></p>
            <p>Пример: <code>/{page_name}?date=2024-01-01&label=Мой%20счетчик&color=blue</code></p>
            """, 404
        
        # Создаем временный счетчик на основе параметров URL
        try:
            color_hex, _ = parse_color(url_color if url_color else 'blue')
            target_date = parse_date(url_date)
            label = url_label if url_label else f'Счетчик {page_name}'
        except Exception as e:
            return f"<h1>Ошибка создания счетчика</h1><p>{e}</p>", 400
    
    # Позволяем переопределить параметры через URL (даже для предустановленных счетчиков)
    if url_date:
        try:
            target_date = parse_date(url_date)
        except Exception as e:
            print(f"Ошибка парсинга даты из URL: {e}")
    
    if url_label:
        label = url_label
    
    if url_color:
        try:
            color_hex, _ = parse_color(url_color)
        except Exception as e:
            print(f"Ошибка парсинга цвета из URL: {e}")
    
    # Вычисляем разницу в днях
    today = date.today()
    days_diff = (today - target_date).days
    
    # Разбираем цвет на составляющие для CSS
    if '-' in color_hex:
        color_start, color_end = color_hex.split('-')
    else:
        # Если цвет не в формате градиента, используем дефолтный
        color_start, color_end = '#667eea', '#764ba2'
    
    # Создаем контекст
    context = {
        'days_diff': days_diff,
        'target_date': target_date.strftime('%d.%m.%Y'),
        'today': today.strftime('%d.%m.%Y'),
        'label': label,
        'color_start': color_start,
        'color_end': color_end,
        'page_name': page_name,
    }
    
    return render_template('index.html', **context)

def add_counter(page_name, date_str, label, color):
    """Добавляет постоянный счетчик в словарь"""
    color_hex, color_name = parse_color(color)
    COUNTERS[page_name] = {
        'date': parse_date(date_str),
        'label': label,
        'color': color_hex,
        'color_name': color_name
    }

def main():
    """Точка входа"""
    global COUNTERS
    
    parser = argparse.ArgumentParser(
        description='Минималистичный счетчик дней с настраиваемой подписью и цветом фона',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры цветов:
  blue   - синий градиент
  green  - зеленый градиент
  orange - оранжевый градиент  
  purple - фиолетовый градиент
  red    - красный градиент

Или свои цвета в формате hex:
  "#667eea-#764ba2"
  "#ff0000-#00ff00"

Два режима работы:
  1. Постоянные счетчики (через --counter):
     python app.py --counter terraform 2024-01-01 "Дней без аварий" purple
     Счетчики сохраняются и отображаются на главной странице.
  
  2. Временные счетчики (через URL):
     http://localhost:5000/terraform?date=2023-01-01&label=Дней%20без%20аварий&color=purple
     http://localhost:5000/terraform?date=2023-01-01&label=Дней%20без%20проблем&color=%23000000-%23ffffff
     Счетчики создаются только на время запроса, не сохраняются.

Примеры использования:
  python app.py --counter terraform 2024-01-01 "Terraform:" purple
  python app.py --host 0.0.0.0 --port 5000  # для временных счетчиков
        """
    )
    
    parser.add_argument('--counter', nargs=4, action='append',
                       metavar=('ИМЯ', 'ДАТА', 'НАДПИСЬ', 'ЦВЕТ'),
                       help='Добавить постоянный счетчик: --counter <имя_страницы> <дата> <надпись> <цвет>')
    
    default_host = os.getenv('HOST', '0.0.0.0')
    default_port = int(os.getenv('PORT', '5000'))
    
    parser.add_argument('--host', type=str, default=default_host,
                       help=f'Хост (по умолчанию: {default_host})')
    parser.add_argument('--port', '-p', type=int, default=default_port,
                       help=f'Порт (по умолчанию: {default_port})')
    
    args = parser.parse_args()
    
    # Добавляем постоянные счетчики, если они указаны
    if args.counter:
        for counter_data in args.counter:
            page_name, date_str, label, color = counter_data
            add_counter(page_name, date_str, label, color)
    
    print(f"🚀 Мульти-счетчик дней")
    
    if COUNTERS:
        print(f"📊 Постоянных счетчиков: {len(COUNTERS)}")
        print("\n📋 Список постоянных счетчиков:")
        print("-" * 60)
        
        for page_name, counter_data in COUNTERS.items():
            print(f"🔗 /{page_name}")
            print(f"   📅 Дата отсчета: {counter_data['date'].strftime('%d.%m.%Y')}")
            print(f"   🏷️  Надпись: '{counter_data['label']}'")
            print(f"   🎨 Цвет: {counter_data.get('color_name', 'Пользовательский')}")
            print()
        print(f"🌐 Главная страница: http://{args.host}:{args.port}")
    else:
        print("✨ Режим временных счетчиков")
        print("💡 Счетчики создаются только при обращении по URL")
        print(f"🌐 Главная страница: http://{args.host}:{args.port}")
    
    print("\n🎛️  Создание временного счетчика через URL:")
    print(f"    http://{args.host}:{args.port}/ИМЯ?date=ДАТА&label=НАДПИСЬ&color=ЦВЕТ")
    print("\n📌 Примеры:")
    print(f"    http://{args.host}:{args.port}/terraform?date=2024-01-01&label=Дней%20без%20аварий&color=purple")
    print(f"    http://{args.host}:{args.port}/k8s?date=2023-06-15&label=Дней%20без%20инцидентов&color=green")
    print("\n🛑 Для остановки нажмите Ctrl+C")
    
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == '__main__':
    main()