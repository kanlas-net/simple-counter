# Базовая команда
docker run -p 5000:5000 days-counter --date 2024-01-01

# С другим портом
docker run -p 8080:5000 days-counter --date 2024-01-01

# С переменными окружения
docker run -p 5000:5000 -e PORT=5000 -e HOST=0.0.0.0 days-counter --date 2024-01-01

# Дата в прошлом
docker run -p 5000:5000 days-counter --date 2024-01-01

# Дата в будущем (отрицательное число)
docker run -p 5000:5000 days-counter --date 2026-01-01

# Сегодняшняя дата
docker run -p 5000:5000 days-counter --date $(date +%Y-%m-%d)

# Вчерашняя дата
docker run -p 5000:5000 days-counter --date $(date -d "yesterday" +%Y-%m-%d)