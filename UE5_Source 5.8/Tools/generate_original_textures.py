#!/usr/bin/env python3
"""Generate original, deterministic gothic PBR textures for Noble Archimedes.

The output is intentionally *not* stored in the repository. Run this script to a
staging directory, inspect the results, then import them with
`ue5_import_generated_textures.py`.

Examples:
    python Tools/generate_original_textures.py --out C:/Projects/NobleArchimedes/ArtSource/GeneratedTextures
    python Tools/generate_original_textures.py --size 512 --only limestone,walnut
    python Tools/generate_original_textures.py --size 1024 --only lava

The recipes are generic procedural material studies (noise, brick bonds, Voronoi
cracks, weave, grain, veins). No pixels or layouts from the local reference pack
are read or reused.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

TAU = math.pi * 2.0


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def clamp01(x):
    return np.clip(x, 0.0, 1.0)


def smoothstep(edge0, edge1, x):
    if edge0 == edge1:
        return (x >= edge1).astype(np.float32)
    t = clamp01((x - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def color(rgb):
    return np.array(rgb, dtype=np.float32) / 255.0


def fft_noise(shape, feature=64.0, seed=0, beta=2.0):
    """Tileable band-limited noise using a periodic FFT basis."""
    h, w = shape
    rng = np.random.default_rng(seed)
    field = rng.normal(size=(h, w)).astype(np.float32)
    fy = np.fft.fftfreq(h).astype(np.float32)[:, None]
    fx = np.fft.fftfreq(w).astype(np.float32)[None, :]
    freq = np.sqrt(fx * fx + fy * fy)
    freq[0, 0] = 1.0
    spectrum = np.fft.fft2(field)
    # Low-pass with a soft feature-size cutoff and a 1/f rolloff.
    spectrum *= np.exp(-(freq * float(feature)) ** 2)
    spectrum /= (freq + 1e-6) ** beta
    out = np.real(np.fft.ifft2(spectrum)).astype(np.float32)
    out -= out.min()
    out /= max(out.max(), 1e-6)
    return out


def fbm(shape, feature=64.0, octaves=5, seed=0, persistence=0.5):
    result = np.zeros(shape, dtype=np.float32)
    amplitude = 1.0
    total = 0.0
    f = float(feature)
    for i in range(octaves):
        result += amplitude * fft_noise(shape, max(f, 2.0), seed + i * 101, beta=1.6)
        total += amplitude
        amplitude *= persistence
        f *= 0.5
    return result / max(total, 1e-6)


def voronoi(shape, cells=40, seed=0):
    """Return (F1, F2-F1) for a wrapped Voronoi field."""
    h, w = shape
    rng = np.random.default_rng(seed)
    pts = rng.random((cells, 2)) * np.array([h, w], dtype=np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    f1 = np.full((h, w), 1e9, dtype=np.float32)
    f2 = np.full((h, w), 1e9, dtype=np.float32)
    for py, px in pts:
        dy = np.abs(yy - py)
        dy = np.minimum(dy, h - dy)
        dx = np.abs(xx - px)
        dx = np.minimum(dx, w - dx)
        d = np.sqrt(dx * dx + dy * dy)
        closer = d < f1
        f2 = np.where(closer, f1, np.minimum(f2, d))
        f1 = np.where(closer, d, f1)
    f1 /= max(h, w)
    f2 /= max(h, w)
    return f1.astype(np.float32), (f2 - f1).astype(np.float32)


def brick_field(shape, rows, cols, mortar=0.05, offset=0.5, seed=0):
    """Return (height, mortar_mask, per_brick_hash) for a running-bond pattern."""
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = yy / h * rows
    row = np.floor(v).astype(np.int32)
    u = xx / w * cols + (row % 2) * offset
    col = np.floor(u).astype(np.int32)
    fx = u - col
    fy = v - row
    edge = np.minimum.reduce([fx, 1.0 - fx, fy, 1.0 - fy])
    # Normalize the edge distance into a bevel height.
    bevel = smoothstep(0.0, mortar * 2.0, edge)
    mortar_mask = (edge < mortar).astype(np.float32)
    # Stable pseudo-random value per brick.
    hv = np.sin(row * 12.9898 + col * 78.233 + seed * 0.017) * 43758.5453
    hv = hv - np.floor(hv)
    return (0.55 + 0.45 * bevel).astype(np.float32), mortar_mask, hv.astype(np.float32)


def scratches(shape, count=90, seed=0, length=(20, 180), width=1):
    h, w = shape
    rng = np.random.default_rng(seed)
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    for _ in range(count):
        x0, y0 = rng.integers(0, w), rng.integers(0, h)
        ang = rng.random() * TAU
        ln = rng.integers(length[0], length[1])
        x1 = int(x0 + math.cos(ang) * ln)
        y1 = int(y0 + math.sin(ang) * ln)
        # Draw wrapped copies so the scratch field tiles.
        for ox in (-w, 0, w):
            for oy in (-h, 0, h):
                draw.line((x0 + ox, y0 + oy, x1 + ox, y1 + oy), fill=255, width=width)
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))
    return np.asarray(mask, dtype=np.float32) / 255.0


def normal_from_height(height, strength=4.0):
    dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * 0.5
    dy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * 0.5
    nx = -dx * strength
    ny = -dy * strength
    nz = np.ones_like(height)
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.stack([nx * inv, ny * inv, nz * inv], axis=-1).astype(np.float32)


def ao_from_height(height, radius=5, strength=0.55):
    # A cheap local-occlusion approximation: low areas receive less ambient light.
    lo = np.asarray(
        Image.fromarray((height * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(radius)
        ), dtype=np.float32) / 255.0
    return clamp01(0.72 + 0.28 * (height - lo) * 2.0 + 0.18 * height).astype(np.float32)


def save_rgb(path, rgb):
    arr = (clamp01(rgb) * 255.0 + 0.5).astype(np.uint8)
    Image.fromarray(arr, "RGB").save(path, optimize=True)


def save_rgba(path, rgb, alpha):
    arr = np.concatenate([clamp01(rgb), clamp01(alpha)[..., None]], axis=-1)
    arr = (arr * 255.0 + 0.5).astype(np.uint8)
    Image.fromarray(arr, "RGBA").save(path, optimize=True)


def save_normal(path, n):
    save_rgb(path, n * 0.5 + 0.5)


def save_orm(path, ao, roughness, metallic):
    orm = np.stack([
        clamp01(ao),
        clamp01(roughness),
        np.full_like(ao, clamp01(metallic)),
    ], axis=-1)
    save_rgb(path, orm)


def write_set(out_root, family, albedo, height, roughness, metallic,
              emissive=None, normal_strength=4.0, alpha=None):
    folder = Path(out_root) / family
    folder.mkdir(parents=True, exist_ok=True)
    n = normal_from_height(height, normal_strength)
    ao = ao_from_height(height)
    if alpha is None:
        save_rgb(folder / ("T_%s_A.png" % family), albedo)
    else:
        save_rgba(folder / ("T_%s_A.png" % family), albedo, alpha)
    save_normal(folder / ("T_%s_N.png" % family), n)
    save_orm(folder / ("T_%s_ORM.png" % family), ao, roughness, metallic)
    if emissive is not None:
        save_rgb(folder / ("T_%s_E.png" % family), emissive)
    return folder


# ---------------------------------------------------------------------------
# Recipes
# ---------------------------------------------------------------------------

def make_limestone(size, seed):
    shape = (size, size)
    height, mortar, hv = brick_field(shape, rows=rand_rows(size, seed, 4, 6),
                                     cols=rand_cols(size, seed, 3, 5),
                                     mortar=0.045, seed=seed)
    grain = fbm(shape, feature=18, octaves=6, seed=seed + 1)
    coarse = fbm(shape, feature=90, octaves=4, seed=seed + 2)
    cracks = smoothstep(0.025, 0.0, voronoi(shape, cells=18, seed=seed + 3)[1]) * 0.35
    height = clamp01(0.62 * height + 0.28 * grain + 0.10 * coarse - cracks)
    base = color((128, 122, 112))
    shade = 0.72 + 0.30 * height[..., None] + 0.10 * (hv[..., None] - 0.5)
    albedo = base * shade
    # Mortar is darker and slightly warmer.
    albedo = lerp(albedo, color((74, 68, 61)), mortar[..., None] * 0.55)
    # Damp/moss in the low areas.
    moss = smoothstep(0.42, 0.72, fbm(shape, feature=32, octaves=5, seed=seed + 4)) * (1.0 - height)
    albedo = lerp(albedo, color((56, 74, 47)), moss[..., None] * 0.34)
    rough = 0.80 + 0.12 * (1.0 - height) + 0.04 * grain
    return albedo, height, rough, 0.0, None, 4.0


def rand_rows(size, seed, lo, hi):
    rng = np.random.default_rng(seed + 9001)
    return int(rng.integers(lo, hi + 1))


def rand_cols(size, seed, lo, hi):
    rng = np.random.default_rng(seed + 9002)
    return int(rng.integers(lo, hi + 1))


def make_soot_brick(size, seed):
    shape = (size, size)
    height, mortar, hv = brick_field(shape, rows=rand_rows(size, seed, 7, 10),
                                     cols=rand_cols(size, seed, 3, 5),
                                     mortar=0.06, seed=seed)
    grain = fbm(shape, feature=12, octaves=6, seed=seed + 1)
    soot = fbm(shape, feature=55, octaves=5, seed=seed + 2)
    height = clamp01(0.60 * height + 0.30 * grain - 0.10 * smoothstep(0.55, 0.8, soot))
    base = color((92, 70, 57))
    shade = 0.68 + 0.32 * height[..., None] + 0.16 * (hv[..., None] - 0.5)
    albedo = base * shade
    albedo = lerp(albedo, color((42, 36, 32)), mortar[..., None] * 0.75)
    albedo = lerp(albedo, color((28, 26, 24)), smoothstep(0.45, 0.82, soot)[..., None] * 0.35)
    albedo = lerp(albedo, color((72, 78, 50)), smoothstep(0.62, 0.85, grain)[..., None] * 0.10)
    rough = 0.82 + 0.12 * (1.0 - height) + 0.04 * grain
    return albedo, height, rough, 0.0, None, 5.0


def make_slate(size, seed):
    shape = (size, size)
    height, mortar, hv = brick_field(shape, rows=3, cols=3, mortar=0.025, seed=seed)
    grain = fbm(shape, feature=9, octaves=6, seed=seed + 1)
    broad = fbm(shape, feature=70, octaves=4, seed=seed + 2)
    scratch = scratches(shape, count=120, seed=seed + 3, length=(18, 120), width=1)
    cracks = smoothstep(0.018, 0.0, voronoi(shape, cells=14, seed=seed + 4)[1]) * 0.55
    height = clamp01(0.60 * height + 0.25 * grain + 0.10 * broad - 0.16 * scratch - cracks)
    base = color((70, 78, 88))
    shade = 0.68 + 0.30 * height[..., None] + 0.12 * (hv[..., None] - 0.5)
    albedo = base * shade
    albedo = lerp(albedo, color((38, 43, 50)), mortar[..., None] * 0.6)
    albedo = lerp(albedo, color((96, 103, 111)), smoothstep(0.55, 0.9, broad)[..., None] * 0.12)
    rough = 0.52 + 0.24 * (1.0 - height) + 0.06 * grain
    return albedo, height, rough, 0.0, None, 3.5


def make_rose_marble(size, seed):
    shape = (size, size)
    turb = fbm(shape, feature=52, octaves=5, seed=seed + 1)
    fine = fbm(shape, feature=13, octaves=4, seed=seed + 2)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = xx / size
    v = yy / size
    veins = np.abs(np.sin((u * 5.0 + v * 3.0 + turb * 4.5) * TAU))
    veins = smoothstep(0.10, 0.0, veins)
    veins2 = np.abs(np.sin((u * 9.0 - v * 5.0 + turb * 6.0) * TAU))
    veins2 = smoothstep(0.06, 0.0, veins2) * 0.6
    height = clamp01(0.45 + 0.18 * fine - 0.25 * (veins + veins2))
    base = color((158, 143, 154))
    albedo = base * (0.78 + 0.16 * turb[..., None] + 0.08 * fine[..., None])
    albedo = lerp(albedo, color((94, 82, 96)), (veins + veins2)[..., None] * 0.55)
    albedo = lerp(albedo, color((196, 186, 192)), smoothstep(0.6, 0.95, turb)[..., None] * 0.25)
    rough = 0.18 + 0.12 * (1.0 - height) + 0.04 * fine
    return albedo, height, rough, 0.0, None, 2.0


def make_walnut(size, seed):
    shape = (size, size)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = xx / size
    v = yy / size
    warp = fbm(shape, feature=48, octaves=5, seed=seed + 1)
    rings = 0.5 + 0.5 * np.sin((v * 18.0 + warp * 2.2) * TAU)
    grain = fbm(shape, feature=6, octaves=5, seed=seed + 2)
    pores = smoothstep(0.72, 0.95, fbm(shape, feature=3, octaves=3, seed=seed + 3))
    height = clamp01(0.55 + 0.25 * rings + 0.15 * grain - 0.18 * pores)
    base = color((92, 59, 38))
    shade = 0.55 + 0.42 * height[..., None] + 0.10 * (grain[..., None] - 0.5)
    albedo = base * shade
    albedo = lerp(albedo, color((44, 27, 18)), (1.0 - rings)[..., None] * 0.32)
    albedo = lerp(albedo, color((132, 90, 55)), smoothstep(0.15, 0.0, rings)[..., None] * 0.18)
    rough = 0.38 + 0.20 * (1.0 - height) + 0.04 * grain
    return albedo, height, rough, 0.0, None, 3.0


def make_blackened_iron(size, seed):
    shape = (size, size)
    dents = fbm(shape, feature=56, octaves=5, seed=seed + 1)
    grain = fbm(shape, feature=7, octaves=5, seed=seed + 2)
    scratch = scratches(shape, count=150, seed=seed + 3, length=(10, 100), width=1)
    rust = smoothstep(0.54, 0.80, fbm(shape, feature=22, octaves=5, seed=seed + 4))
    height = clamp01(0.55 + 0.18 * dents + 0.18 * grain - 0.22 * scratch)
    base = color((60, 64, 70))
    albedo = base * (0.62 + 0.38 * height[..., None])
    albedo = lerp(albedo, color((94, 56, 32)), rust[..., None] * 0.55)
    albedo = lerp(albedo, color((120, 126, 132)), smoothstep(0.6, 0.9, scratch)[..., None] * 0.25)
    rough = 0.28 + 0.18 * rust + 0.10 * (1.0 - height) + 0.04 * grain
    return albedo, height, rough, 1.0, None, 3.5


def make_gold_trim(size, seed):
    shape = (size, size)
    grain = fbm(shape, feature=18, octaves=5, seed=seed + 1)
    tarnish = smoothstep(0.45, 0.78, fbm(shape, feature=40, octaves=5, seed=seed + 2))
    scratch = scratches(shape, count=70, seed=seed + 3, length=(12, 90), width=1)
    height = clamp01(0.62 + 0.18 * grain - 0.12 * tarnish - 0.10 * scratch)
    base = color((198, 154, 66))
    albedo = base * (0.72 + 0.26 * height[..., None])
    albedo = lerp(albedo, color((112, 78, 37)), tarnish[..., None] * 0.45)
    albedo = lerp(albedo, color((232, 204, 118)), smoothstep(0.7, 0.95, scratch)[..., None] * 0.30)
    rough = 0.20 + 0.14 * tarnish + 0.08 * (1.0 - height) + 0.03 * grain
    return albedo, height, rough, 1.0, None, 2.0


def make_crimson_velvet(size, seed):
    shape = (size, size)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = xx / size
    v = yy / size
    fine_weave = 0.5 + 0.25 * np.sin(u * TAU * 96.0) + 0.25 * np.sin(v * TAU * 96.0)
    fold = fbm(shape, feature=42, octaves=5, seed=seed + 1)
    fiber = fbm(shape, feature=5, octaves=4, seed=seed + 2)
    height = clamp01(0.45 + 0.20 * fine_weave + 0.25 * fold + 0.10 * fiber)
    base = color((112, 31, 38))
    albedo = base * (0.50 + 0.48 * height[..., None])
    albedo = lerp(albedo, color((48, 12, 17)), smoothstep(0.55, 0.82, fold)[..., None] * 0.30)
    albedo = lerp(albedo, color((154, 76, 72)), smoothstep(0.12, 0.0, fold)[..., None] * 0.15)
    rough = 0.64 + 0.16 * (1.0 - height) + 0.04 * fiber
    return albedo, height, rough, 0.0, None, 2.0


def make_carpet(size, seed):
    """Rough, matte carpet cloth with a subtle weave and flat normals.

    The flat normal is intentional: a fine normal map on a long, thin runner
    aliases badly under point lights and reads as bright stripes.
    """
    shape = (size, size)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = xx / size
    v = yy / size
    fine_weave = 0.5 + 0.25 * np.sin(u * TAU * 48.0) + 0.25 * np.sin(v * TAU * 48.0)
    fiber = fbm(shape, feature=6, octaves=3, seed=seed + 1)
    height = np.full(shape, 0.5, dtype=np.float32)
    base = color((98, 20, 26))
    albedo = base * (0.78 + 0.16 * fine_weave[..., None] + 0.06 * fiber[..., None])
    albedo = lerp(albedo, color((44, 8, 12)), (1.0 - fine_weave)[..., None] * 0.12)
    rough = 0.90 + 0.04 * fiber
    return albedo, height, rough, 0.0, None, 0.0


def make_moss(size, seed):
    shape = (size, size)
    clumps = fbm(shape, feature=24, octaves=6, seed=seed + 1)
    fine = fbm(shape, feature=4, octaves=4, seed=seed + 2)
    leaf = smoothstep(0.42, 0.78, clumps) * (0.6 + 0.4 * fine)
    height = clamp01(0.35 + 0.45 * clumps + 0.20 * fine)
    base = color((48, 76, 38))
    albedo = base * (0.65 + 0.50 * leaf[..., None])
    albedo = lerp(albedo, color((82, 104, 46)), smoothstep(0.6, 0.9, fine)[..., None] * 0.35)
    albedo = lerp(albedo, color((32, 44, 25)), (1.0 - height)[..., None] * 0.45)
    rough = 0.82 + 0.10 * (1.0 - height)
    return albedo, height, rough, 0.0, None, 2.5


def make_water(size, seed):
    shape = (size, size)
    flow1 = fbm(shape, feature=40, octaves=5, seed=seed + 1)
    flow2 = fbm(shape, feature=14, octaves=5, seed=seed + 2)
    ripple = 0.5 + 0.5 * np.sin((flow1 * 5.0 + flow2 * 3.0) * TAU)
    height = clamp01(0.45 + 0.35 * ripple + 0.20 * flow2)
    base = color((26, 70, 92))
    albedo = base * (0.60 + 0.35 * ripple[..., None])
    albedo = lerp(albedo, color((54, 132, 148)), smoothstep(0.55, 0.9, flow2)[..., None] * 0.22)
    rough = 0.06 + 0.10 * ripple + 0.04 * flow2
    return albedo, height, rough, 0.0, None, 1.5


def make_ice(size, seed):
    shape = (size, size)
    crack = smoothstep(0.03, 0.0, voronoi(shape, cells=22, seed=seed + 1)[1])
    crack2 = smoothstep(0.015, 0.0, voronoi(shape, cells=55, seed=seed + 2)[1]) * 0.5
    frost = fbm(shape, feature=10, octaves=5, seed=seed + 3)
    height = clamp01(0.55 + 0.20 * frost - 0.35 * (crack + crack2))
    base = color((132, 174, 192))
    albedo = base * (0.72 + 0.25 * height[..., None])
    albedo = lerp(albedo, color((212, 236, 242)), crack[..., None] * 0.55)
    albedo = lerp(albedo, color((62, 102, 128)), (1.0 - frost)[..., None] * 0.20)
    rough = 0.12 + 0.16 * (1.0 - height) + 0.04 * frost
    return albedo, height, rough, 0.0, None, 2.0


def make_lava(size, seed):
    shape = (size, size)
    f1, edge = voronoi(shape, cells=15, seed=seed + 1)
    cracks = smoothstep(0.035, 0.0, edge)
    heat = fbm(shape, feature=28, octaves=5, seed=seed + 2)
    height = clamp01(0.30 + 0.20 * f1 + 0.10 * fbm(shape, feature=8, octaves=4, seed=seed + 3) - 0.18 * cracks)
    rock = color((36, 28, 25))
    albedo = rock * (0.55 + 0.45 * height[..., None])
    albedo = lerp(albedo, color((78, 34, 18)), smoothstep(0.5, 0.9, heat)[..., None] * 0.25)
    emissive = np.zeros((size, size, 3), dtype=np.float32)
    glow = clamp01(cracks * (0.6 + 0.7 * heat))
    emissive[..., 0] = glow * 1.0
    emissive[..., 1] = glow * 0.28
    emissive[..., 2] = glow * 0.03
    rough = 0.42 + 0.20 * (1.0 - height) + 0.08 * heat
    return albedo, height, rough, 0.0, emissive, 2.0


def make_decal_cracks(size, seed):
    shape = (size, size)
    f1, edge = voronoi(shape, cells=20, seed=seed + 1)
    main = smoothstep(0.035, 0.0, edge)
    fine = smoothstep(0.012, 0.0, voronoi(shape, cells=60, seed=seed + 2)[1]) * 0.55
    alpha = clamp01(main + fine)
    height = clamp01(0.35 + 0.25 * f1 - 0.20 * alpha)
    albedo = np.zeros((size, size, 3), dtype=np.float32)
    albedo[..., 0] = 0.055
    albedo[..., 1] = 0.050
    albedo[..., 2] = 0.045
    rough = np.full((size, size), 0.78, dtype=np.float32)
    return albedo, height, rough, 0.0, None, 3.0, alpha


def make_decal_moss(size, seed):
    shape = (size, size)
    clumps = fbm(shape, feature=32, octaves=6, seed=seed + 1)
    holes = fbm(shape, feature=6, octaves=4, seed=seed + 2)
    alpha = smoothstep(0.42, 0.72, clumps) * smoothstep(0.18, 0.45, holes)
    height = clamp01(0.30 + 0.55 * clumps + 0.15 * holes)
    base = color((48, 76, 38))
    albedo = base * (0.65 + 0.55 * height[..., None])
    albedo = lerp(albedo, color((92, 116, 52)), smoothstep(0.6, 0.9, holes)[..., None] * 0.35)
    rough = 0.82 + 0.10 * (1.0 - height)
    return albedo, height, rough, 0.0, None, 2.5, alpha


RECIPES = {
    "limestone": make_limestone,
    "soot_brick": make_soot_brick,
    "slate": make_slate,
    "rose_marble": make_rose_marble,
    "walnut": make_walnut,
    "blackened_iron": make_blackened_iron,
    "gold_trim": make_gold_trim,
    "crimson_velvet": make_crimson_velvet,
    "carpet": make_carpet,
    "moss": make_moss,
    "water": make_water,
    "ice": make_ice,
    "lava": make_lava,
    "decal_cracks": make_decal_cracks,
    "decal_moss": make_decal_moss,
}


def build(family, size, seed, out_root):
    func = RECIPES[family]
    result = func(size, seed)
    albedo, height, rough, metallic, emissive, normal_strength = result[:6]
    alpha = result[6] if len(result) > 6 else None
    folder = write_set(out_root, family, albedo, height, rough, metallic,
                       emissive=emissive, normal_strength=normal_strength,
                       alpha=alpha)
    print("wrote %-18s %s" % (family, folder))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=r"C:\Projects\NobleArchimedes\ArtSource\GeneratedTextures")
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20261019)
    parser.add_argument("--only", default="", help="comma-separated recipe names")
    args = parser.parse_args(argv)

    chosen = [x.strip() for x in args.only.split(",") if x.strip()] or list(RECIPES)
    unknown = [x for x in chosen if x not in RECIPES]
    if unknown:
        raise SystemExit("unknown recipes: %s" % ", ".join(unknown))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for i, family in enumerate(chosen):
        build(family, args.size, args.seed + i * 31, out)
    print("done: %d texture sets -> %s" % (len(chosen), out))


if __name__ == "__main__":
    main()
