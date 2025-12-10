#!/usr/bin/env python3
"""
Минималистичный счетчик дней с настраиваемой подписью
"""

from flask import Flask, render_template
from datetime import datetime, date
import argparse
import sys
import os

app = Flask(__name__)

# Глобальные переменные
DEFAULT_DATE = None
CUSTOM_LABEL = None

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
    """Главная страница - только счетчик с настраиваемой подписью"""
    global DEFAULT_DATE, CUSTOM_LABEL
    
    if not DEFAULT_DATE:
        DEFAULT_DATE = date.today()
    
    if not CUSTOM_LABEL:
        CUSTOM_LABEL = "Дней прошло:"
    
    # Вычисляем разницу в днях
    today = date.today()
    days_diff = (today - DEFAULT_DATE).days
    
    # Создаем контекст
    context = {
        'days_diff': days_diff,
        'target_date': DEFAULT_DATE.strftime('%d.%m.%Y'),
        'today': today.strftime('%d.%m.%Y'),
        'label': CUSTOM_LABEL
    }
    
    return render_template('index.html', **context)

@app.route('/health')
def health():
    """Health check для Docker/Kubernetes"""
    return {'status': 'healthy', 'service': 'days-counter'}

def main():
    """Точка входа"""
    global DEFAULT_DATE, CUSTOM_LABEL
    
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(
        description='Минималистичный счетчик дней с настраиваемой подписью',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python app.py --date 2024-01-01 --label "Дней с Нового Года:"
  python app.py --date 2023-06-15 --label "Дней работы:"
  python app.py --date 2024-01-01 --label "📅 Прошло дней:"
        """
    )
    
    parser.add_argument('--date', '-d', type=str, required=True, 
                       help='Дата отсчета в формате ГГГГ-ММ-ДД')
    
    parser.add_argument('--label', '-l', type=str, default="Дней прошло:",
                       help='Надпись над счетчиком (по умолчанию: "Дней прошло:")')
    
    # Аргументы хоста и порта - с дефолтами из переменных окружения
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
    
    print(f"🚀 Минималистичный счетчик дней")
    print(f"📅 Дата отсчета: {DEFAULT_DATE.strftime('%d.%m.%Y')}")
    print(f"🏷️  Надпись: '{CUSTOM_LABEL}'")
    print(f"🔢 Отображается только число дней")
    print(f"🌐 Адрес: http://{args.host}:{args.port}")
    print(f"❤️  Health check: http://{args.host}:{args.port}/health")
    print("\n🛑 Для остановки нажмите Ctrl+C")
    
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == '__main__':
    main()