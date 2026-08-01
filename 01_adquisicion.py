
import os
import time
import csv
import numpy as np
from pycromanager import Core
from datetime import datetime
from pathlib import Path
import tifffile
from tqdm import tqdm

# === MENÚ DE MEDICIÓN ===
print("=== MENÚ DE MEDICIÓN ===")
print("Seleccione qué desea medir:")
print("1. LED individual")
print("2. LED doble")
print("3. Línea")
print("4. Línea doble")
print("5. Esquina")
print("6. Par, Impar o Todo")  # <-- ACTUALIZADO
print("7. Esquinas dobles")
print("8. Cruz")  # <-- NUEVA OPCIÓN

tipos = {
    1: "LED",
    2: "LED doble",
    3: "Línea",
    4: "Línea doble",
    5: "Esquina",
    6: "Par, Impar o Todo",  # <-- ACTUALIZADO
    7: "Esquinas dobles",
    8: "Cruz"  # <-- NUEVA OPCIÓN
}

opcion = int(input("Ingrese una opción (1-8): "))  # <-- ACTUALIZADO

# Subopciones para ciertas opciones
if opcion == 6:
    print("Seleccione subopción:")
    print("1. Par")
    print("2. Impar")
    print("3. Todo")
    subopcion = int(input("Ingrese subopción (1-3): "))
    if subopcion == 1:
        numero = "Par"
    elif subopcion == 2:
        numero = "Impar"
    elif subopcion == 3:
        numero = "Todo"
    else:
        print("⚠️ Subopción inválida. Se asignará 'desconocida'.")
        numero = "desconocida"
elif opcion == 7:
    print("Seleccione subopción de Esquinas dobles:")
    print("1. 1-4")
    print("2. 2-3")
    subopcion = int(input("Ingrese subopción (1 o 2): "))
    if subopcion == 1:
        numero = "1-4"
    elif subopcion == 2:
        numero = "2-3"
    else:
        print("⚠️ Subopción inválida. Se asignará 'desconocida'.")
        numero = "desconocida"
else:
    numero = input(f"Ingrese el número o identificador para {tipos.get(opcion, 'Tipo desconocido')}: ")

nombre_tipo = tipos.get(opcion, "Tipo desconocido")
corriente = input("Ajuste la corriente y luego ingrese su valor EXACTAMENTE como en la lista (ej: 10 mA): ").strip()

# === Generar tiempos por corriente ===
def generar_tiempos(corriente):
    personalizados = {
        "10 mA": np.arange(0, 0.5 + 0.001, 0.05),
        "5 mA": np.arange(0, 0.5 + 0.001, 0.05),
        "1 mA": np.arange(0, 1 + 0.001, 0.05),
        "0.5 mA": np.arange(1, 2 + 0.001, 0.05),
        "0.1 mA": np.arange(5, 10 + 0.001, 0.05),
        "0.05 mA": np.arange(10, 20 + 0.001, 0.05),
        "0.01 mA": np.arange(50, 150 + 0.001, 0.05)
    }

    criticos = {
        "10 mA": [],
        "5 mA": [0.6, 0.7, 0.8, 0.9, 1, 2, 3, 4, 5, 10, 50, 100, 150, 200, 300, 400, 500, 800, 1000],
        "1 mA": [0.1, 0.5, 1, 2, 3, 5, 10, 20, 50, 100, 200, 300, 400, 500, 800, 1000],
        "0.5 mA": [0.1, 0.5, 1, 1.5, 1.8, 2, 3, 4, 5, 10, 50, 100, 200, 300, 400, 500, 800, 1000],
        "0.1 mA": [0.5, 1, 5, 10, 25, 50, 100, 200, 300, 400, 500, 800, 1000],
        "0.05 mA": [1, 5, 10, 20, 30, 50, 100, 200, 300, 400, 500, 800, 1000],
        "0.01 mA": [1, 5, 10, 15, 20, 30, 40, 300, 400, 500, 800, 1000]
    }

    comun = np.arange(0, 500 + 1, 20)

    tiempos = set()
    tiempos.update(personalizados.get(corriente, []))
    tiempos.update(criticos.get(corriente, []))
    tiempos.update(comun)

    return sorted(set(round(float(t), 2) for t in tiempos if t > 0))

tiempos_exposicion = generar_tiempos(corriente)

# === Configuración de entorno ===
desktop = Path.home() / "Desktop"
base_dir = os.path.join(desktop, "Medidas Script x2")
os.makedirs(base_dir, exist_ok=True)

core = Core()
if core.is_sequence_running():
    core.stop_sequence_acquisition()

core.set_camera_device("HamamatsuHam_DCAM")
print("✅ Cámara configurada correctamente.")

nombre_sesion = f"{nombre_tipo} {numero} {corriente}"
ruta_sesion = os.path.join(base_dir, nombre_sesion)
os.makedirs(ruta_sesion, exist_ok=True)

print(f"📁 Las imágenes se guardarán en: {ruta_sesion}")

csv_path = os.path.join(ruta_sesion, f"{nombre_sesion}_registro.csv")
with open(csv_path, mode='w', newline='') as f_csv:
    writer = csv.writer(f_csv)
    writer.writerow(["Nombre archivo", "Corriente", "Exposición (ms)", "Ruta", "Fecha"])

# === Adquisición ===
print(f"🎯 Iniciando adquisición de {len(tiempos_exposicion)} imágenes...")

for tiempo in tqdm(tiempos_exposicion):
    nombre_archivo = f"{nombre_tipo} {numero} {corriente} {tiempo} ms"
    ruta_imagen = os.path.join(ruta_sesion, f"{nombre_archivo}.tif")

    core.set_exposure(float(tiempo))
    time.sleep(0.5)

    if core.is_sequence_running():
        core.stop_sequence_acquisition()

    core.snap_image()
    raw = core.get_image()

    try:
        imagen = raw.reshape((512, 640))
        if imagen is not None and imagen.size > 0 and np.max(imagen) > 0:
            tifffile.imwrite(ruta_imagen, imagen)
            with open(csv_path, mode='a', newline='') as f_csv:
                writer = csv.writer(f_csv)
                writer.writerow([nombre_archivo, corriente, tiempo, ruta_imagen, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        else:
            print(f"⚠️ Imagen vacía: {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error en {nombre_archivo}: {e}")
