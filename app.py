#!/usr/bin/env python3
"""
Минималистичный счетчик дней с настраиваемой подписью и цветом фона
"""

from flask import Flask, render_template, request
from datetime import datetime, date
import argparse
import sys
import os

app = Flask(__name__)

# Глобальные переменные
DEFAULT_DATE = None
CUSTOM_LABEL = None
BACKGROUND_COLOR = None

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
    """Парсит цвет из строки"""
    color_str = color_str.strip().lower()
    
    # Предопределенные градиенты
    gradients = {
        'blue': '#667eea-#764ba2',
        'green': '#11998e-#38ef7d',
        'orange': '#f46b45-#eea849',
        'purple': '#8a2be2-#da70d6',
        'red': '#ff416c-#ff4b2b',
        'sunset': '#ff7e5f-#feb47b',
        'ocean': '#2193b0-#6dd5ed',
        'forest': '#56ab2f-#a8e063',
        'berry': '#8e2de2-#4a00e0',
    }
    
    # Если это предопределенный градиент
    if color_str in gradients:
        return gradients[color_str]
    
    # Если это hex цвета (например, #667eea-#764ba2)
    if '-' in color_str:
        parts = color_str.split('-')
        if len(parts) == 2:
            import re
            hex_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
            if hex_pattern.match(parts[0]) and hex_pattern.match(parts[1]):
                return color_str
    
    # По умолчанию синий градиент
    return gradients['blue']

@app.route('/')
def index():
    """Главная страница - только счетчик"""
    global DEFAULT_DATE, CUSTOM_LABEL, BACKGROUND_COLOR
    
    # Получаем параметры из URL или используем дефолтные
    url_date = request.args.get('date')
    url_label = request.args.get('label')
    url_color = request.args.get('color')
    
    target_date = DEFAULT_DATE
    label = CUSTOM_LABEL
    color = BACKGROUND_COLOR
    
    # Обновляем из параметров URL
    if url_date:
        try:
            target_date = parse_date(url_date)
        except:
            pass
    
    if url_label:
        label = url_label
    
    if url_color:
        try:
            color = parse_color(url_color)
        except:
            pass
    
    # Устанавливаем дефолтные значения
    if not target_date:
        target_date = date.today()
    
    if not label:
        label = "Дней прошло:"
    
    if not color:
        color = parse_color('blue')
    
    # Вычисляем разницу в днях
    today = date.today()
    days_diff = (today - target_date).days
    
    # Разбираем цвет на составляющие для CSS
    color_start, color_end = color.split('-')
    
    # Создаем контекст
    context = {
        'days_diff': days_diff,
        'target_date': target_date.strftime('%d.%m.%Y'),
        'today': today.strftime('%d.%m.%Y'),
        'label': label,
        'color_start': color_start,
        'color_end': color_end,
    }
    
    return render_template('index.html', **context)

def main():
    """Точка входа"""
    global DEFAULT_DATE, CUSTOM_LABEL, BACKGROUND_COLOR
    
    parser = argparse.ArgumentParser(
        description='Минималистичный счетчик дней с настраиваемой подписью и цветом фона',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры цветов:
  blue   - синий градиент (по умолчанию)
  green  - зеленый градиент
  orange - оранжевый градиент  
  purple - фиолетовый градиент
  red    - красный градиент

Или свои цвета в формате hex:
  "#667eea-#764ba2"
  "#ff0000-#00ff00"

Примеры использования:
  python app.py --date 2024-01-01 --label "Новый Год:" --color red
  python app.py --date 2023-06-15 --color green
        """
    )
    
    parser.add_argument('--date', '-d', type=str, required=True, 
                       help='Дата отсчета в формате ГГГГ-ММ-ДД')
    
    parser.add_argument('--label', '-l', type=str, default="Дней прошло:",
                       help='Надпись над счетчиком')
    
    parser.add_argument('--color', '-c', type=str, default="blue",
                       help='Цвет фона (предустановки или hex цвета)')
    
    default_host = os.getenv('HOST', '0.0.0.0')
    default_port = int(os.getenv('PORT', '5000'))
    
    parser.add_argument('--host', type=str, default=default_host,
                       help=f'Хост (по умолчанию: {default_host})')
    parser.add_argument('--port', '-p', type=int, default=default_port,
                       help=f'Порт (по умолчанию: {default_port})')
    
    args = parser.parse_args()
    
    # Устанавливаем значения
    DEFAULT_DATE = parse_date(args.date)
    CUSTOM_LABEL = args.label
    BACKGROUND_COLOR = parse_color(args.color)
    
    color_start, color_end = BACKGROUND_COLOR.split('-')
    
    print(f"🚀 Счетчик дней")
    print(f"📅 Дата отсчета: {DEFAULT_DATE.strftime('%d.%m.%Y')}")
    print(f"🏷️  Надпись: '{CUSTOM_LABEL}'")
    print(f"🎨 Цвет фона: {args.color}")
    print(f"🌐 Адрес: http://{args.host}:{args.port}")
    print("\n🛑 Для остановки нажмите Ctrl+C")
    
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == '__main__':
    main()