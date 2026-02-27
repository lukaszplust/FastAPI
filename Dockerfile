# obraz Pythona
FROM python:3.10-slim

# ustawiam folder roboczy wewnątrz kontenera
WORKDIR /app

# kopiuje listę bibliotek i instaluje je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# kopiuje całą resztę kodu (main.py, database.py itd.)
COPY . .

# otwieram port 8000
EXPOSE 8000

# komenda, która uruchomi serwer po starcie kontenera
# "0.0.0.0" - to nasluchiwanie na wszystkich adresach
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]