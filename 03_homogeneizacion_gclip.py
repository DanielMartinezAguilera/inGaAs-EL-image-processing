# -*- coding: utf-8 -*-
"""
Extensión G_CLIP + Plot de g (float) reanudable.
- Recorre 'Homogenea' buscando ... f.tif (ya ponderadas con la máscara de pesos).
- Calcula C (media global o en LEDs si existe labels_uint16.tif).
- Obtiene g_raw = C / f (float32) y h = C (plano exacto).
- Exporta (modo completo por defecto):
    * g_xy_GCLIP_float32.tif        (g real en float32)
    * g_xy_GCLIP_14bit.tif (o 16 bit si --bits 16)
    * g_xy_GCLIP_3D_inferno.png     (superficie 3D visual mapeada)
    * g_xy_GCLIP_meta.txt           (relación entre plot visual y escala; G_CLIP usado)
    * h_xy_C_14bit.tif              (plano C en 14/16 bits)
    * h_xy_C_3D_inferno.png         (superficie 3D del plano)
    * g_xy_FLOAT_3D_inferno.png     (NUEVO: superficie 3D de g en float real)
- REANUDABLE: si los ficheros existen, salta; con --overwrite fuerza recálculo.
- Modo rápido (--only-float-plot): solo genera g_xy_FLOAT_3D_inferno.png sin tocar nada más.
"""

from __future__ import annotations
import argparse, re, sys
from pathlib import Path
import numpy as np

# IO
try:
    import tifffile as tiff
except Exception as e:
    print("Falta tifffile (pip install tifffile).", e); sys.exit(1)

# Plot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

# Progreso
try:
    from tqdm import tqdm
    PROG = lambda it, **kw: tqdm(it, **kw)
except Exception:
    def PROG(it, total=None, desc=""):
        print(f"[...] {desc}  (sin tqdm)")
        for x in it:
            yield x

# ---------- Utilidades ----------

def parse_I_T_from_path(p: Path):
    """Extrae I (mA) y T (ms) de la ruta usando regex tolerante (coma/punto)."""
    s = str(p)
    I = T = None
    mI = re.search(r'([0-9]+[.,]?[0-9]*)\\s*mA', s, re.IGNORECASE)
    mT = re.search(r'([0-9]+[.,]?[0-9]*)\\s*ms', s, re.IGNORECASE)
    if mI: I = float(mI.group(1).replace(',', '.'))
    if mT: T = float(mT.group(1).replace(',', '.'))
    return I, T

def list_exposures(in_root: Path, filter_text: str|None):
    """Devuelve lista de (exp_dir, f_path, labels_path|None)."""
    f_candidates = sorted(in_root.rglob("* f.tif"))
    exps = []
    for fp in f_candidates:
        if filter_text and filter_text.lower() not in str(fp).lower():
            continue
        exp_dir = fp.parent
        labels = exp_dir / "labels_uint16.tif"
        if not labels.exists():
            labels = None
        exps.append((exp_dir, fp, labels))
    return exps

def compute_C(f_u16: np.ndarray, labels_u16: np.ndarray|None, mode: str):
    """Devuelve C (float) en unidades de f (cuentas 14/16-bit) según modo."""
    arr = f_u16.astype(np.float32)
    if mode.lower() == "leds" and labels_u16 is not None:
        leds_mask = labels_u16 > 0
        vals = arr[leds_mask]
        if vals.size >= 10:
            return float(np.mean(vals))
    # fallback (global)
    return float(np.mean(arr))

def save_tiff_u16(path: Path, arr_u16: np.ndarray):
    path.parent.mkdir(parents=True, exist_ok=True)
    tiff.imwrite(str(path), arr_u16.astype(np.uint16), photometric='minisblack')

def save_tiff_float32(path: Path, arr_f: np.ndarray):
    path.parent.mkdir(parents=True, exist_ok=True)
    tiff.imwrite(str(path), arr_f.astype(np.float32))

def plot_surface_inferno(path_png: Path, Z: np.ndarray, title: str, zlabel: str):
    """Plot 3D (inferno)."""
    H, W = Z.shape
    X, Y = np.meshgrid(np.arange(W), np.arange(H))
    fig = plt.figure(figsize=(8.5, 7.0))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='inferno', linewidth=0, antialiased=True)
    ax.set_title(title)
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel(zlabel)
    fig.colorbar(surf, shrink=0.75, aspect=18, label=zlabel)
    path_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(str(path_png), dpi=150)
    plt.close(fig)

def map_to_bits_with_clip(arr_float: np.ndarray, bits: int, gclip: float):
    """Mapeo puntual (NO filtro): u = clip(arr/gclip,0,1) * (2^N-1)."""
    maxv = (1 << bits) - 1
    with np.errstate(divide='ignore', invalid='ignore'):
        norm = arr_float / float(gclip)
    norm = np.clip(norm, 0.0, 1.0)
    return (norm * maxv + 0.5).astype(np.uint16), maxv

# ---------- Principal ----------

def main():
    p = argparse.ArgumentParser(description="Extensión G_CLIP (g_raw visual + h=C) + plot 3D de g (float)")
    p.add_argument("--root", default=r"C:\\Users\\danic\\OneDrive\\Escritorio\\Homogenea",
                   help="Raíz IN/OUT (por defecto tu carpeta Homogenea)")
    p.add_argument("--filter", default=None, help="Texto que debe aparecer en la ruta de la exposición")
    p.add_argument("--I", type=float, default=None, help="Intensidad mA a filtrar (si se desea)")
    p.add_argument("--T", type=float, default=None, help="Tiempo ms a filtrar (si se desea)")
    p.add_argument("--tolI", type=float, default=1e-6, help="Tolerancia mA")
    p.add_argument("--tolT", type=float, default=1e-3, help="Tolerancia ms")
    p.add_argument("--Cfrom", choices=["global","leds"], default="leds", help="Cómo estimar C")
    p.add_argument("--gclip", type=float, default=4.0, help="Tope de visualización G_CLIP (no es filtro)")
    p.add_argument("--bits", type=int, choices=[14,16], default=14, help="Profundidad de salida visual")
    p.add_argument("--maxn", type=int, default=None, help="Máximo nº de exposiciones (debug)")
    p.add_argument("--overwrite", action="store_true", help="Recalcular aunque existan salidas")
    p.add_argument("--only-float-plot", action="store_true",
                   help="Solo generar g_xy_FLOAT_3D_inferno.png (reanudable), sin tocar el resto")
    args = p.parse_args()

    IN_ROOT = Path(args.root)
    if not IN_ROOT.exists():
        print(f"No existe la ruta raíz: {IN_ROOT}"); sys.exit(1)

    exps = list_exposures(IN_ROOT, args.filter)
    # Filtro por I/T si procede
    if args.I is not None or args.T is not None:
        exps_f = []
        for (exp_dir, f_path, labels_path) in exps:
            I, T = parse_I_T_from_path(exp_dir)
            ok = True
            if args.I is not None and (I is None or abs(I - args.I) > args.tolI):
                ok = False
            if args.T is not None and (T is None or abs(T - args.T) > args.tolT):
                ok = False
            if ok: exps_f.append((exp_dir, f_path, labels_path))
        exps = exps_f

    if not exps:
        print("No se encontraron exposiciones con '... f.tif' bajo Homogenea (con los filtros dados).")
        return

    if args.maxn is not None:
        exps = exps[:args.maxn]

    desc = "Plot 3D g(float)" if args.only_float_plot else "G_CLIP g_raw+h=C + plot float"
    print(f"Procesando {len(exps)} exposiciones bajo {IN_ROOT}  |  bits={args.bits}  G_CLIP={args.gclip}  Cfrom={args.Cfrom}")

    for (exp_dir, f_path, labels_path) in PROG(exps, total=len(exps), desc=desc):
        out_g_float = exp_dir / "g_xy_GCLIP_float32.tif"
        out_g_u   = exp_dir / (f"g_xy_GCLIP_{args.bits}bit.tif")
        out_g_png = exp_dir / "g_xy_GCLIP_3D_inferno.png"
        out_g_meta= exp_dir / "g_xy_GCLIP_meta.txt"
        out_h_u   = exp_dir / (f"h_xy_C_{args.bits}bit.tif")
        out_h_png = exp_dir / "h_xy_C_3D_inferno.png"
        out_g_float_png = exp_dir / "g_xy_FLOAT_3D_inferno.png"  # NUEVO
        done_flag = exp_dir / "_DONE_GCLIP.ok"

        if args.only_float_plot:
            # Solo generar el PNG de float. Reanudar si existe.
            if out_g_float_png.exists() and not args.overwrite:
                continue
            # Cargar g float; si no existe, calcularlo mínimo.
            if out_g_float.exists():
                g_raw = tiff.imread(str(out_g_float)).astype(np.float32)
            else:
                f_u16 = tiff.imread(str(f_path)).astype(np.uint16)
                labels = tiff.imread(str(labels_path)).astype(np.uint16) if labels_path and labels_path.exists() else None
                C = compute_C(f_u16, labels, args.Cfrom)
                with np.errstate(divide='ignore', invalid='ignore'):
                    g_raw = C / f_u16.astype(np.float32)
                save_tiff_float32(out_g_float, g_raw)  # cache para el futuro
            # Plot 3D del float (sin textos extra)
            Z = g_raw.copy()
            Z[~np.isfinite(Z)] = np.nan
            plot_surface_inferno(out_g_float_png, Z, title="Superficie: g_raw (float)", zlabel="g")
            continue

        # --- MODO COMPLETO ---
        if not args.overwrite:
            if all(p.exists() for p in [out_g_float, out_g_u, out_g_png, out_g_meta, out_h_u, out_h_png, out_g_float_png, done_flag]):
                continue

        # Carga f y labels
        f_u16 = tiff.imread(str(f_path)).astype(np.uint16)
        H, W = f_u16.shape
        labels = tiff.imread(str(labels_path)).astype(np.uint16) if labels_path and labels_path.exists() else None

        # Cálculo de C
        C = compute_C(f_u16, labels, args.Cfrom)

        # g_raw float y guardado
        with np.errstate(divide='ignore', invalid='ignore'):
            g_raw = C / f_u16.astype(np.float32)  # Infs donde f=0
        save_tiff_float32(out_g_float, g_raw)

        # h plano en 14/16 bit
        h_plane_u16 = np.full((H, W), int(round(max(0, min(C, (1<<args.bits)-1)))), dtype=np.uint16)
        save_tiff_u16(out_h_u, h_plane_u16)

        # g visual con G_CLIP (no filtro)
        g_u16, _ = map_to_bits_with_clip(g_raw, bits=args.bits, gclip=args.gclip)
        save_tiff_u16(out_g_u, g_u16)

        # Plots 3D (inferno): visual y float
        plot_surface_inferno(out_g_png, g_u16.astype(np.float32),
                             title="Superficie: g_raw visual (G_CLIP)",
                             zlabel=f"Valor {args.bits}-bit (G_CLIP={args.gclip})")
        Z = g_raw.copy(); Z[~np.isfinite(Z)] = np.nan
        plot_surface_inferno(out_g_float_png, Z,
                             title="Superficie: g_raw (float)",
                             zlabel="g")
        plot_surface_inferno(out_h_png, h_plane_u16.astype(np.float32),
                             title="Superficie: h = C",
                             zlabel=f"Intensidad {args.bits}-bit")

        # Metadatos del mapeo de g
        finite = np.isfinite(g_raw)
        stats = {
            "C_value": float(C),
            "bits": int(args.bits),
            "G_CLIP": float(args.gclip),
            "g_min": float(np.nanmin(g_raw[finite])) if np.any(finite) else float("nan"),
            "g_max": float(np.nanmax(g_raw[finite])) if np.any(finite) else float("nan"),
            "p95":   float(np.nanpercentile(g_raw[finite], 95)) if np.any(finite) else float("nan"),
            "p99":   float(np.nanpercentile(g_raw[finite], 99)) if np.any(finite) else float("nan"),
            "num_pixels": int(g_raw.size),
            "num_finite": int(np.count_nonzero(finite)),
            "num_zero_in_f": int(np.count_nonzero(f_u16 == 0)),
            "num_saturated_visual": int(np.count_nonzero(g_raw >= args.gclip)),
        }
        out_g_meta.parent.mkdir(parents=True, exist_ok=True)
        with open(out_g_meta, "w", encoding="utf-8") as fh:
            fh.write("# Mapeo de visualización (NO filtro): u = clip(g/G_CLIP,0,1) * (2^N-1)\n")
            for k,v in stats.items():
                fh.write(f"{k}: {v}\n")

        # Marca de completado
        done_flag.write_text("OK\n", encoding="utf-8")

    print("Terminado.")

if __name__ == "__main__":
    main()
