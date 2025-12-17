# Run python app
python app.py \
  --counter incident1 2024-01-01 "Дней без аварий" purple \
  --counter incident2 2025-01-01 "Дней без проблем" '#000000-#ffffff' \
  --host 0.0.0.0 --port 5000

# Run in docker
docker run -p 5000:5000 ghcr.io/kanlas-net/simple-counter \
  --counter incident1 2024-01-01 "Дней без аварий" purple \
  --counter incident2 2025-01-01 "Дней без проблем" '#000000-#ffffff'

# Create counter dynamically by url
http://localhost:5000/terraform?date=2023-01-01&label=Дней%20без%20аварий&color=purple
http://localhost:5000/terraform?date=2023-01-01&label=Дней%20без%20проблем&color=%23000000-%23ffffff