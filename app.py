#!/usr/bin/env python3
"""
Минималистичный счетчик дней - только цифра
"""

from flask import Flask, render_template
from datetime import datetime, date
import argparse
import sys

app = Flask(__name__)

# Глобальная переменная для даты отсчета
DEFAULT_DATE = None

def parse_date(date_str):
    """Парсит дату из строки"""
    try:
        # Пробуем основные форматы
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y.%m.%d'):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Неверный формат даты: {date_str}")
    except Exception as e:
        print(f"Ошибка парсинга даты: {e}")
        sys.exit(1)

@app.route('/')
def index():
    """Главная страница - только счетчик"""
    global DEFAULT_DATE
    
    if not DEFAULT_DATE:
        DEFAULT_DATE = date.today()
    
    # Вычисляем разницу в днях
    today = date.today()
    days_diff = (today - DEFAULT_DATE).days
    
    # Создаем минимальный контекст
    context = {
        'days_diff': days_diff,
        'target_date': DEFAULT_DATE.strftime('%d.%m.%Y'),
        'today': today.strftime('%d.%m.%Y')
    }
    
    return render_template('index.html', **context)

def main():
    """Точка входа"""
    global DEFAULT_DATE
    
    parser = argparse.ArgumentParser(description='Минималистичный счетчик дней')
    parser.add_argument('--date', '-d', type=str, required=True, 
                       help='Дата отсчета в формате ГГГГ-ММ-ДД')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Хост (по умолчанию: 127.0.0.1)')
    parser.add_argument('--port', '-p', type=int, default=5000,
                       help='Порт (по умолчанию: 5000)')
    
    args = parser.parse_args()
    
    # Парсим дату
    DEFAULT_DATE = parse_date(args.date)
    
    print(f"🚀 Минималистичный счетчик дней")
    print(f"📅 Дата отсчета: {DEFAULT_DATE.strftime('%d.%m.%Y')}")
    print(f"🔢 Отображается только число дней")
    print(f"🌐 Адрес: http://{args.host}:{args.port}")
    print("\n🛑 Для остановки нажмите Ctrl+C")
    
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == '__main__':
    main()