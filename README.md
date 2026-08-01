# inGaAs-EL-image-processing
Python pipeline for automated InGaAs image acquisition, matrix processing, and 3D EL characterization (UVa Bachelor's Thesis).

# Write README.md (English version)
readme_en = """# Electroluminescence (EL) Image Acquisition and Processing System

>  *Read this in [Español](./README.es.md)*

This repository contains the source code for automated image acquisition, matrix processing, and photometric analysis developed as part of the Bachelor's Thesis by **Daniel Martínez Aguilera** at the **University of Valladolid (UVa)**. The work falls within the fields of Applied Physics, Electronics, and Photonics.

---

##  Abstract

This work presents the development and validation of an experimental system for the acquisition and processing of images applied to electroluminescence (EL). It should be noted that the work does not involve EL measurements on photovoltaic panels; instead, a custom-designed infrared LED matrix has been employed as a controlled reference source to calibrate and correct the response of the InGaAs camera.

The setup includes both the electronic design of the matrix and the integration of the InGaAs camera together with auxiliary devices in a controlled environment, enabling the acquisition of reproducible images under different current and exposure conditions. A homogenization procedure based on irradiance-weighted masks has been implemented, supported by a fully automated processing workflow in Python.

This framework computes representative functions of the spatial intensity distribution, along with linear profiles and three-dimensional representations, allowing for a thorough analysis of the uniformity and reliability of the system. As a result, a significant improvement in image quality has been achieved, establishing a reproducible methodology that contributes to the advanced study of optical characterization techniques in the photovoltaic and optoelectronic fields.

---

##  Software Structure & Pipeline

The repository organizes the complete workflow into three Python modules designed to be executed sequentially:

1. **`01_adquisicion.py` — Acquisition and Hardware Control Module:**
   * Automated mass image capture integrated with Micro-Manager (`pycromanager`) and an InGaAs sensor.
   * Interactive control of emission patterns (single LEDs, lines, matrices, corners, crosses) and adaptive exposure time generation based on drive current.
   * Automated metadata logging and raw `.tif` image export.

2. **`02_procesamiento_3d.py` — Processing and 3D Reconstruction Module:**
   * Parallelized image series processing (`ProcessPoolExecutor`).
   * Matrix conversion to CSV files and 3D surface intensity (ADU) mapping using high-definition colormaps (`hot`).

3. **`03_homogeneizacion_gclip.py` — Advanced Photometric & Homogenization Module:**
   * Calculation of reference constants ($C$) across region of interest (LED ROI) or global averages.
   * Computation of floating-point gain/correction matrices ($g = C / f$).
   * Contrast clipping ($G\_CLIP$), 14/16-bit normalization, and 3D surface map extraction using `inferno` colormap with statistical metric exports.

---

>  **IMPORTANT:** The scripts are specifically designed to interface with the laboratory's experimental setup architecture and local file directory structures.

---

##  Attached Documentation

* [`Resumen_1pag.pdf`](./Resumen_1pag.pdf) – Executive summary.
* [`Presentacion_TFG.pdf`](./docs/Presentacion_TFG.pdf) – Thesis defense presentation slides.
* [`Memoria_TFG.pdf`](./docs/Memoria_TFG.pdf) – Full Bachelor's Thesis manuscript.
"""

# Write README.es.md (Spanish version)
readme_es = """# Sistema de Adquisición y Procesado de Imágenes de Electroluminiscencia (EL)

>  *Leer esto en [English](./README.md)*

Este repositorio contiene el código fuente para la automatización de capturas, el procesamiento matricial y el análisis fotométrico desarrollado en el ámbito del Trabajo de Fin de Grado por **Daniel Martínez Aguilera** para la **Universidad de Valladolid (UVa)**. Específicamente, se centra en las áreas de Física Aplicada, Electrónica y Fotónica.

---

##  Resumen

En el presente trabajo se desarrolla y valida un sistema experimental para la adquisición y procesado de imágenes con aplicación a electroluminiscencia (EL). Conviene señalar que no se ha estudiado la EL en paneles fotovoltaicos, sino que se ha empleado una matriz de LEDs infrarrojos como fuente de referencia controlada para calibrar y corregir la respuesta de la cámara InGaAs.

El montaje incluye tanto el diseño electrónico de la propia matriz como la integración de una cámara InGaAs y un conjunto de dispositivos auxiliares en un entorno controlado, lo que ha permitido obtener imágenes reproducibles bajo distintas condiciones de corriente y tiempo de exposición. Sobre estas imágenes se ha implementado un procedimiento de homogeneización basado en la aplicación de pesos derivados de medidas de irradiancia, acompañado de un flujo de procesado totalmente automatizado mediante scripts en Python.

Dicho procesado permite calcular funciones representativas de la distribución espacial de la intensidad, junto con perfiles lineales y representaciones tridimensionales, facilitando un análisis exhaustivo de la uniformidad y fiabilidad del sistema. Como resultado, se ha alcanzado una mejora significativa en la calidad de las imágenes y se ha establecido una metodología reproducible que contribuye al estudio avanzado de técnicas de caracterización óptica en el ámbito fotovoltaico y optoelectrónico.

---

##  Estructura del Software y Pipeline

El repositorio organiza el flujo completo de trabajo en tres módulos en Python ejecutables en secuencia:

1. **`01_adquisicion.py` — Módulo de Adquisición y Control:**
   * Automatización de capturas masivas mediante integración con Micro-Manager (`pycromanager`) y cámara InGaAs.
   * Modulación interactiva de patrones de emisión (LEDs, líneas, matrices, esquinas, cruces) y generación adaptativa de tiempos de exposición según la corriente aplicada.
   * Registro automatizado de metadatos y exportación de imágenes `.tif` brutas.

2. **`02_procesamiento_3d.py` — Módulo de Procesamiento y Reconstrucción 3D:**
   * Procesamiento en paralelo de las series de imágenes capturadas (`ProcessPoolExecutor`).
   * Conversión matricial a CSV y generación de superficies 3D de distribución de intensidad (ADU) mediante mapas de color (`hot`).

3. **`03_homogeneizacion_gclip.py` — Módulo Fotométrico Avanzado y Homogeneización:**
   * Cálculo de constantes de referencia ($C$) sobre regiones de interés (ROI de LEDs) o medias globales.
   * Generación de matrices de ganancia/corrección en precisión flotante ($g = C / f$).
   * Mapeo de contraste ($G\_CLIP$), normalización a 14/16 bits y extracción de mapas de superficie en escala `inferno` con exportación de métricas estadísticas.

---

>  **IMPORTANTE:** Los scripts están diseñados para operar sincronizados con la arquitectura del setup experimental y la infraestructura de hardware/directorios del laboratorio.

---

##  Documentación Adjunta

* [`Resumen_1pag.pdf`](./Resumen_1pag.pdf) – Resumen ejecutivo del trabajo.
* [`Presentacion_TFG.pdf`](./docs/Presentacion_TFG.pdf) – Diapositivas de la defensa.
* [`Memoria_TFG.pdf`](./docs/Memoria_TFG.pdf) – Memoria completa del Trabajo de Fin de Grado.
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_en)

with open("README.es.md", "w", encoding="utf-8") as f:
    f.write(readme_es)

print("Files README.md and README.es.md successfully created.")
