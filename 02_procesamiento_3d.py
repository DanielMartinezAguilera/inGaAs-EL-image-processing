
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import imageio.v3 as iio
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

def procesar_imagen(args):
    ruta_entrada, ruta_relativa, salida_base = args
    try:
        ruta_salida = os.path.join(salida_base, os.path.dirname(ruta_relativa))
        os.makedirs(ruta_salida, exist_ok=True)

        img = iio.imread(ruta_entrada)
        alto, ancho = img.shape
        nombre_base = os.path.splitext(os.path.basename(ruta_entrada))[0].replace(" ", "_")

        # CSV global
        csv_path = os.path.join(ruta_salida, f"{nombre_base}_completa.csv")
        pd.DataFrame(img).to_csv(csv_path, index=False, header=False)

        # Surface 3D visualización mejorada
        Y, X = np.meshgrid(np.arange(alto), np.arange(ancho), indexing='ij')
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, img, cmap='hot', edgecolor='none', antialiased=True, rstride=1, cstride=1)
        ax.view_init(elev=35, azim=225)
        ax.set_box_aspect([1, 1, 0.5])
        ax.set_title(f"Hipersuperficie 3D - {nombre_base}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Intensidad (ADU)")
        ax.set_zlim(0, np.max(img))
        plt.tight_layout()
        plt.savefig(os.path.join(ruta_salida, f"{nombre_base}_surface_3D.png"), dpi=300)
        plt.close()

        return f"✅ Procesado: {ruta_relativa}"

    except Exception as e:
        return f"❌ Error en {ruta_relativa}: {e}"


if __name__ == "__main__":
    entrada_base = r"C:\Users\danic\Desktop\Medidas Script x2"
    salida_base = r"C:\Users\danic\Desktop\Gamma x2"

    tareas = []
    for root, _, files in os.walk(entrada_base):
        for file in files:
            if file.lower().endswith(".tif"):
                ruta_entrada = os.path.join(root, file)
                ruta_relativa = os.path.relpath(ruta_entrada, entrada_base)
                tareas.append((ruta_entrada, ruta_relativa, salida_base))

    with ProcessPoolExecutor() as executor:
        for resultado in tqdm(executor.map(procesar_imagen, tareas), total=len(tareas), desc="Procesando imágenes 3D mejoradas"):
            print(resultado)
