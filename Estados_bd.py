import sys
import random
from datetime import datetime, timedelta
import pyodbc

def conectar_sqlserver():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=DESKTOP-QTOME2L;'
            'DATABASE=ACME_EV;'
            'Trusted_Connection=yes;'
        )
        return conn
    except pyodbc.Error as e:
        print("Error al conectar a SQL Server:", e)
        sys.exit(1)

def insertar_registros(conn, id_dispositivo_str, cantidad):
    ahora = datetime.now()
    kilometros_actuales = random.randint(0, 1000)
    cursor = conn.cursor()

    for i in range(cantidad):
        timestamp = ahora + timedelta(seconds=i*59)
        fecha_hora = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        estado_carga = random.randint(0, 100)
        onoff = random.randint(0, 1)

        # 95% de los estados serán '000'
        if random.random() < 0.95:
            estado = 0
        else:
            estado = random.randint(1, 999)

        if onoff == 1:
            kilometros_actuales += random.randint(0, 3)

        # Insertar el registro en la tabla
        try:
            cursor.execute("""
                INSERT INTO ESTADOS (IdDispositivo, FechaHora, EstadoCarga, OnOff, Estado, Kilometros)
                VALUES (?, ?, ?, ?, ?, ?)
            """, id_dispositivo_str, fecha_hora, estado_carga, onoff, f"{estado:03d}", kilometros_actuales)
            conn.commit()
        except pyodbc.Error as e:
            print(f"Error al insertar registro {i}: {e}")
            conn.rollback()
            sys.exit(1)

    conn.commit()
    print(f"{cantidad} registros insertados exitosamente en la base de datos.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python generador_estados_sqlserver.py <IdDispositivo> <CantidadRegistros>")
        sys.exit(1)

    try:
        id_dispositivo = int(sys.argv[1])
        cantidad_registros = int(sys.argv[2])
        conexion = conectar_sqlserver()
        id_dispositivo_str = f"VIN{str(id_dispositivo).zfill(5)}"
        insertar_registros(conexion, id_dispositivo_str, cantidad_registros)
        conexion.close()
    except ValueError:
        print("Error: los argumentos deben ser enteros.")
        sys.exit(1)
