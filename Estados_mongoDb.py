import sys
import random
from datetime import datetime, timedelta
#pip install pymongo
from pymongo import MongoClient

def conectar_mongodb():
    try:
        cliente = MongoClient("mongodb://localhost:27017/")
        db = cliente["ACME_EV"]
        coleccion = db["Estados"]
        return coleccion
    except Exception as e:
        print("Error al conectar a MongoDB:", e)
        sys.exit(1)

def insertar_en_mongodb(coleccion, id_dispositivo_str, cantidad):
    ahora = datetime.now()
    kilometros_actuales = random.randint(0, 1000)

    for i in range(cantidad):
        timestamp = ahora + timedelta(seconds=i * 59)
        fecha_hora = timestamp  # se almacena como tipo datetime en MongoDB

        estado_carga = random.randint(0, 100)
        onoff = random.randint(0, 1)

        estado = 0 if random.random() < 0.95 else random.randint(1, 999)

        if onoff == 1:
            kilometros_actuales += random.randint(0, 3)

        filtro = {
            "IdDispositivo": id_dispositivo_str,
            "FechaHora": fecha_hora
        }

        # Eliminar cualquier documento duplicado antes de insertar
        coleccion.delete_many(filtro)

        documento = {
            "IdDispositivo": id_dispositivo_str,
            "FechaHora": fecha_hora,
            "EstadoCarga": estado_carga,
            "OnOff": onoff,
            "Estado": f"{estado:03d}",
            "Kilometros": kilometros_actuales
        }

        try:
            coleccion.insert_one(documento)
            #print(f"Insertado: {documento}")
        except Exception as e:
            print(f"Error al insertar documento: {e}")
            sys.exit(1)

    print(f"{cantidad} documentos insertados exitosamente en MongoDB.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python Estados_mongodb.py <IdDispositivo> <CantidadRegistros>")
        sys.exit(1)

    try:
        id_dispositivo = int(sys.argv[1])
        id_dispositivo_str = f"VIN{str(id_dispositivo).zfill(5)}"
        cantidad_registros = int(sys.argv[2])
        coleccion_estados = conectar_mongodb()
        insertar_en_mongodb(coleccion_estados, id_dispositivo, cantidad_registros)
    except ValueError:
        print("Error: los argumentos deben ser enteros.")
        sys.exit(1)
