import sys
import random
import json
from datetime import datetime, timedelta
#pip install kafka-python
from kafka import KafkaProducer

def conectar_kafka():
    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        return producer
    except Exception as e:
        print("Error al conectar a Kafka:", e)
        sys.exit(1)

def publicar_en_kafka(producer, id_dispositivo: int, cantidad: int, topic: str = "estados"):
    ahora = datetime.now()
    kilometros_actuales = random.randint(0, 1000)

    for i in range(cantidad):
        timestamp = ahora + timedelta(seconds=i * 59)
        fecha_hora = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        estado_carga = random.randint(0, 100)
        onoff = random.randint(0, 1)

        estado = 0 if random.random() < 0.95 else random.randint(1, 999)

        if onoff == 1:
            kilometros_actuales += random.randint(0, 3)

        mensaje = {
            "IdDispositivo": id_dispositivo_str,
            "FechaHora": fecha_hora,
            "EstadoCarga": estado_carga,
            "OnOff": onoff,
            "Estado": f"{estado:03d}",
            "Kilometros": kilometros_actuales
        }

        try:
            producer.send(topic, mensaje)
            #print(f"Mensaje enviado: {mensaje}")
        except Exception as e:
            print(f"Error al enviar mensaje a Kafka: {e}")
            sys.exit(1)

    producer.flush()
    print(f"{cantidad} mensajes enviados exitosamente al topic '{topic}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python Estados_kafka.py <IdDispositivo> <CantidadRegistros>")
        sys.exit(1)

    try:
        id_dispositivo = int(sys.argv[1])
        id_dispositivo_str = f"VIN{str(id_dispositivo).zfill(5)}"
        cantidad_registros = int(sys.argv[2])
        kafka_producer = conectar_kafka()
        publicar_en_kafka(kafka_producer, id_dispositivo_str, cantidad_registros)
        kafka_producer.close()
    except ValueError:
        print("Error: los argumentos deben ser enteros.")
        sys.exit(1)
