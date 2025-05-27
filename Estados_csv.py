import csv
import sys
import random
from datetime import datetime, timedelta

def generar_datos(id_dispositivo_str, cantidad):
    nombre_archivo = f"Estados_{id_dispositivo}.csv"
    registros = []
    ahora = datetime.now()
    kilometros_actuales = random.randint(0, 1000)

    for i in range(cantidad):
        timestamp = ahora + timedelta(seconds=(i*59)) #cada minuto
        fecha_hora = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        estado_carga = random.randint(0, 100)
        onoff = random.randint(0, 1)

        # 95% o más de las veces, Estado = 000
        if random.random() < 0.95:
            estado = 0
        else:
            estado = random.randint(1, 999)

        if onoff == 1:
            incremento = random.randint(0, 3) #Cantidad de kilometros que avanza
            kilometros_actuales += incremento

        registros.append([
            id_dispositivo_str,
            fecha_hora,
            estado_carga,
            onoff,
            f"{estado:03d}",  # formatear a tres dígitos con ceros
            kilometros_actuales
        ])

    with open(nombre_archivo, mode='w', newline='') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["IdDispositivo", "FechaHora", "EstadoCarga", "OnOff", "Estado", "Kilometros"])
        escritor.writerows(registros)

    print(f"{cantidad} registros generados exitosamente en el archivo {nombre_archivo}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python generador_estados.py <IdDispositivo> <CantidadRegistros>")
        sys.exit(1)

    try:
        id_dispositivo = int(sys.argv[1])
        id_dispositivo_str = f"VIN{str(id_dispositivo).zfill(5)}"
        cantidad_registros = int(sys.argv[2])
        generar_datos(id_dispositivo_str, cantidad_registros)
    except ValueError:
        print("Error: los argumentos deben ser enteros.")
        sys.exit(1)
