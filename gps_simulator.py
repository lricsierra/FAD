import random
import threading
import sys
from datetime import datetime, timedelta
import pyodbc
from kafka import KafkaProducer
import json

# Configuración
# Universidad Rafael Landivar 14.594983138640472, -90.48318594944504
LATITUDE_RANGE = (14.5, 14.8)
LONGITUDE_RANGE = (-90.4, -90.2)
NUM_VEHICLES = 1000 #maximo numero de conexiones en SQL Server es 32767
RECORDS_PER_VEHICLE = 2880  # 24 horas, 1 registro cada 30 segundos

# Generar VINs
VEHICLE_VINS = [f"VIN{str(i+1).zfill(5)}" for i in range(NUM_VEHICLES)]

# Simular movimiento coherente en GPS
def move_vehicle(lat, lon):
    delta_lat = random.uniform(-0.0005, 0.0005)
    delta_lon = random.uniform(-0.0005, 0.0005)
    new_lat = max(min(lat + delta_lat, LATITUDE_RANGE[1]), LATITUDE_RANGE[0])
    new_lon = max(min(lon + delta_lon, LONGITUDE_RANGE[1]), LONGITUDE_RANGE[0])
    return new_lat, new_lon

# Función para cada vehículo
def vehicle_simulator(vin, mode):
    lat = random.uniform(*LATITUDE_RANGE)
    lon = random.uniform(*LONGITUDE_RANGE)
    start_time = datetime.now() - timedelta(hours=24)  # Comenzar desde hace 24 horas

    if mode == "sql":
        server = 'DESKTOP-QTOME2L'
        database = 'ACME_EV'
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};'
            f'DATABASE={database};'
            'Trusted_Connection=yes;'
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM sysobjects WHERE name='gps' AND xtype='U'
            )
            CREATE TABLE gps (
                VIN NVARCHAR(20),
                Fecha DATE,
                Hora TIME,
                Latitud FLOAT,
                Longitud FLOAT
            )
        """)
        conn.commit()
    elif mode == "kafka":
        #producer = KafkaProducer(
        #    bootstrap_servers='localhost:9092',
        #    value_serializer=lambda v: str(v).encode('utf-8')
        #)
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        topic = "gps"

    # Generar 2880 registros por vehículo
    for i in range(RECORDS_PER_VEHICLE):
        current_time = start_time + timedelta(seconds=i * 30)
        lat, lon = move_vehicle(lat, lon)
        data = {
            "VIN": vin,
            "Fecha": current_time.strftime("%Y-%m-%d"),
            "Hora": current_time.strftime("%H:%M:%S"),
            "Latitud": round(lat, 6),
            "Longitud": round(lon, 6)
        }

        if mode == "sql":
            cursor.execute("""
                INSERT INTO gps (VIN, Fecha, Hora, Latitud, Longitud)
                VALUES (?, ?, ?, ?, ?)
            """, (data["VIN"], data["Fecha"], data["Hora"], data["Latitud"], data["Longitud"]))
            if i % 5 == 0:
                conn.commit()  # Confirmar cada 5 registros
        elif mode == "kafka":
            producer.send(topic, value=data)

    if mode == "sql":
        conn.commit()
        conn.close()
    elif mode == "kafka":
        producer.flush()

    print(f"Vehículo {vin} completó {RECORDS_PER_VEHICLE} registros.")

def simulate_concurrent_data(mode):
    threads = []
    for vin in VEHICLE_VINS:
        t = threading.Thread(target=vehicle_simulator, args=(vin, mode))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Simulación concurrente completada.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python simulador.py [kafka|sql]")
    else:
        simulate_concurrent_data(sys.argv[1].lower())
