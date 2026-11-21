#!/usr/bin/env python3
"""The rest of the ZMyusic asset family: vectors, SVG sources, TV/Wear,
desktop ICO/ICNS and the iOS preview images. Run from the repo root:

    py branding/make_assets2.py
"""
from __future__ import annotations

import os
import shutil
import struct
import sys

from PIL import Image, ImageDraw, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import make_assets as A

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def R(*p):
    return os.path.join(ROOT, *p)


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("wrote", os.path.relpath(path, ROOT), img.size)


# ---------------------------------------------------------------- vector XML

# The Z + M as stroked capsule segments on the 108dp adaptive canvas. Android
# masks crop to ~66dp, so the ink is scaled into the centre.

def _fg_vector(path, comment):
    segs = A._mark_segments_1024()
    # map the 1024 design box onto the 108dp canvas. The mark's own inset is
    # preserved, then the whole thing is inset again so Android's ~66dp mask
    # crop never nibbles the ink.
    inset = 19.8
    lo, hi = inset, 108.0 - inset
    span = 1024.0

    def m(v):
        return round(lo + v * (hi - lo) / span, 2)

    w = round(A._mark_stroke_1024() * (hi - lo) / span, 2)
    paths = "\n".join(
        f'  <path android:pathData="M{m(ax)},{m(ay)} L{m(bx)},{m(by)}" '
        f'android:strokeColor="#FFFFFFFF" android:strokeWidth="{w}" '
        f'android:strokeLineCap="round" android:strokeLineJoin="round"/>'
        for (ax, ay), (bx, by) in segs
    )
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<!--
  {comment}
-->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
{paths}
</vector>
'''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    print("wrote", os.path.relpath(path, ROOT))


def _logo_vector(path, viewport_w, viewport_h, comment, pad=0.0, dp_w=None, dp_h=None):
    """The Z+M as a stroked mark on a WxH viewport (used for ic_logo.xml).

    `dp_w`/`dp_h` let a caller keep a large design viewport while declaring a
    small intrinsic size, which is what the shared Compose resource does.
    """
    segs = A._mark_segments_1024()
    # the mark's own ink box in the 1024 design space (stroke included)
    bx0, by0, bx1, by1 = A._mark_extent_1024()
    sw, sh = viewport_w, viewport_h
    scale = min(sw / (bx1 - bx0), sh / (by1 - by0)) * (1 - pad)
    ox = (sw - (bx1 - bx0) * scale) / 2 - bx0 * scale
    oy = (sh - (by1 - by0) * scale) / 2 - by0 * scale

    def X(v):
        return round(v * scale + ox, 2)

    def Y(v):
        return round(v * scale + oy, 2)

    w = round(A._mark_stroke_1024() * scale, 2)
    # Android VectorDrawable syntax, not SVG: AAPT2 keeps un-namespaced `d`
    # and `stroke` as raw attributes, which the platform renderer ignores.
    paths = "\n".join(
        f'  <path android:pathData="M{X(ax)},{Y(ay)} L{X(bx)},{Y(by)}" '
        f'android:fillColor="#00000000" android:strokeColor="#FFFFFFFF" '
        f'android:strokeWidth="{w}" '
        f'android:strokeLineCap="round" android:strokeLineJoin="round"/>'
        for (ax, ay), (bx, by) in segs
    )
    declared_w = round(sw) if dp_w is None else dp_w
    declared_h = round(sh) if dp_h is None else dp_h
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<!--
  {comment}
-->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="{declared_w}dp"
    android:height="{declared_h}dp"
    android:viewportWidth="{int(sw)}"
    android:viewportHeight="{int(sh)}">
{paths}
</vector>
'''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    print("wrote", os.path.relpath(path, ROOT))


def _notification_vector(path):
    segs = A._mark_segments_1024()
    bx0, by0, bx1, by1 = A._mark_extent_1024()
    # fit inside a 22dp content box on a 24dp canvas
    size = 22.0
    scale = size / max(bx1 - bx0, by1 - by0)
    ox = (24 - (bx1 - bx0) * scale) / 2 - bx0 * scale
    oy = (24 - (by1 - by0) * scale) / 2 - by0 * scale

    def X(v):
        return round(v * scale + ox, 2)

    def Y(v):
        return round(v * scale + oy, 2)

    w = round(A._mark_stroke_1024() * scale, 2)
    paths = "\n".join(
        f'  <path android:pathData="M{X(ax)},{Y(ay)} L{X(bx)},{Y(by)}" '
        f'android:strokeColor="#FFFFFFFF" android:strokeWidth="{w}" '
        f'android:strokeLineCap="round" android:strokeLineJoin="round"/>'
        for (ax, ay), (bx, by) in segs
    )
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<!--
  Status-bar / notification silhouette of the ZMyusic mark. The system keeps
    only the alpha channel, so the fill is opaque white and the ink sits inside
    the 22dp content box Android expects on a 24dp canvas.
-->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
{paths}
</vector>
'''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    print("wrote", os.path.relpath(path, ROOT))


def _bg_vectors():
    """Wear/reused solid backgrounds (navy gradient) keep their shape."""
    for rel in ("wearos/src/main/res/drawable/ic_launcher_background.xml",):
        src = R("app", "src", "main", "res", "drawable", "ic_launcher_background.xml")
        dst = R(rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        print("copied", os.path.relpath(dst, ROOT))


# ------------------------------------------------------------------ SVG files

MARK_SVG = '''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- The ZMyusic Z+M monogram, as white strokes tinted by the caller. -->
  <g stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="translate({ox} {oy}) scale({s})">
    <path d="{zpath}"/>
    <path d="{mpath}"/>
  </g>
</svg>
'''


def _mark_paths():
    """The Z and M as two SVG path `d` strings in the 1024 design space."""
    seg = A._mark_segments_1024()
    z = seg[0:3]
    m = seg[3:7]

    def d(parts):
        (x0, y0), _ = parts[0]
        out = [f"M{x0:.1f} {y0:.1f}"]
        for a, b in parts:
            out.append(f"L{b[0]:.1f} {b[1]:.1f}")
        return " ".join(out)

    return d(z), d(m)


def _mark_svg(path, w, h, pad=0.08):
    bx0, by0, bx1, by1 = A._mark_extent_1024()
    s = min(w / (bx1 - bx0), h / (by1 - by0)) * (1 - pad)
    ox = (w - (bx1 - bx0) * s) / 2 - bx0 * s
    oy = (h - (by1 - by0) * s) / 2 - by0 * s
    zpath, mpath = _mark_paths()
    txt = MARK_SVG.format(w=w, h=h, sw=round(A._mark_stroke_1024() * s, 2),
                          ox=round(ox, 2), oy=round(oy, 2), s=round(s, 4),
                          zpath=zpath, mpath=mpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    print("wrote", os.path.relpath(path, ROOT))


FAVICON = '''<svg width="1024" height="1024" viewBox="0 0 1024 1024" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="bg" x1="512" y1="0" x2="512" y2="1024" gradientUnits="userSpaceOnUse">
<stop stop-color="#071A3C"/>
<stop offset="1" stop-color="#0B2C63"/>
</linearGradient>
<radialGradient id="glow" cx="0" cy="0" r="1" gradientTransform="translate(512 450) rotate(90) scale(470)" gradientUnits="userSpaceOnUse">
<stop stop-color="#22D3EE" stop-opacity="0.28"/>
<stop offset="1" stop-color="#22D3EE" stop-opacity="0"/>
</radialGradient>
<linearGradient id="mark" x1="260" y1="250" x2="780" y2="800" gradientUnits="userSpaceOnUse">
<stop stop-color="#67E8F9"/>
<stop offset="0.45" stop-color="#22D3EE"/>
<stop offset="1" stop-color="#2563EB"/>
</linearGradient>
<clipPath id="squircle"><rect width="1024" height="1024" rx="230"/></clipPath>
</defs>
<g clip-path="url(#squircle)">
<rect width="1024" height="1024" fill="url(#bg)"/>
<rect width="1024" height="1024" fill="url(#glow)"/>
</g>
<g stroke="url(#mark)" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" fill="none">
<path d="{zpath}"/>
<path d="{mpath}"/>
</g>
</svg>
'''


def _favicon():
    zpath, mpath = _mark_paths()
    return FAVICON.format(sw=round(A._mark_stroke_1024(), 2), zpath=zpath, mpath=mpath)


# ----------------------------------------------------------- ICO / ICNS writer

def write_ico(path, sizes=(16, 24, 32, 48, 64, 128, 256)):
    """A real multi-resolution ICO.

    Pillow's own ICO writer silently drops every entry when the list is built
    from pre-resized images (the bug that shipped a 781-byte, 16x16-only icon),
    so the container is assembled by hand: each size is written as a PNG and
    tagged. PNG-compressed entries are valid ICO members on every supported
    Windows version.
    """
    import io

    pngs = []
    for s in sizes:
        buf = io.BytesIO()
        A.icon(s).convert("RGBA").save(buf, format="PNG")
        pngs.append((s, buf.getvalue()))

    header = struct.pack("<HHH", 0, 1, len(pngs))
    offset = 6 + 16 * len(pngs)
    entries = b""
    body = b""
    for s, data in pngs:
        dim = 0 if s >= 256 else s
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset)
        body += data
        offset += len(data)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(header + entries + body)
    print("wrote", os.path.relpath(path, ROOT), "ICO", [s for s, _ in pngs])


def write_icns(path, master=1024):
    """Minimal ICNS: ic07..ic14 PNG-encoded entries."""
    types = {
        "ic07": 128, "ic08": 256, "ic09": 512, "ic10": 1024,
        "ic11": 32, "ic12": 64, "ic13": 256, "ic14": 512,
    }
    chunks = []
    for tag, px in types.items():
        img = A.icon(px).convert("RGBA")
        tmp = R("branding", "_tmp.png")
        img.save(tmp)
        with open(tmp, "rb") as f:
            data = f.read()
        chunks.append(tag.encode("ascii") + struct.pack(">I", len(data) + 8) + data)
    os.remove(tmp)
    body = b"".join(chunks)
    with open(path, "wb") as f:
        f.write(b"icns" + struct.pack(">I", len(body) + 8) + body)
    print("wrote", os.path.relpath(path, ROOT), "ICNS")


def _ios_preview(size, dark=False, appearance_dark=False):
    """The launcher icon as the iOS preview picker shows it.

    The asset catalog declares these 3x, so `size` is the pixel size of a
    68 pt tile (204). Dark-mode tiles are dimmed a little even for the
    always-dark choices, so every imageset has a distinct dark image rather
    than falling back to its light one.
    """
    if not dark:
        img = A.icon(size)
    else:
        S = size * A.SS
        plate = A._bg_gradient(S, S, A.NAVY_TOP, (4, 16, 40)).convert("RGB")
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        img.paste(plate, (0, 0), A._squircle_mask(S))
        glow = Image.new("L", (S, S), 0)
        ImageDraw.Draw(glow).ellipse([S * 0.04, -S * 0.02, S * 0.96, S * 0.9], fill=52)
        gl = Image.new("RGBA", (S, S), A.CYAN + (0,))
        gl.putalpha(glow)
        img.alpha_composite(gl)
        img.alpha_composite(A._ink_layer(S))
        img = img.resize((size, size), Image.LANCZOS)
    if appearance_dark:
        img = ImageEnhance.Brightness(img).enhance(0.88)
    return img


def main():
    # Vector drawables
    _fg_vector(R("app", "src", "main", "res", "drawable", "ic_launcher_foreground.xml"),
               "The ZMyusic mark. The 108dp canvas keeps the ink inside the 66dp\n    safe zone every launcher mask crops to.")
    _fg_vector(R("wearos", "src", "main", "res", "drawable", "ic_launcher_foreground.xml"),
               "The ZMyusic mark for Wear OS.")
    _logo_vector(R("app", "src", "main", "res", "drawable", "ic_logo.xml"), 28, 24.2,
                 "The ZMyusic mark, drawn as rounded capsules so every renderer\n    (Compose, TV, Wear) shows the same shape. Tinted by the caller.")
    _logo_vector(R("wearos", "src", "main", "res", "drawable", "ic_logo.xml"), 28, 24.2,
                 "The ZMyusic mark for Wear OS.")
    _logo_vector(R("sharedUi", "src", "commonMain", "composeResources", "drawable", "ic_logo.xml"),
                 560, 484,
                 "The ZMyusic mark shared by the Android, TV, Wear and desktop UIs.\n"
                 "    Tinted by the caller.",
                 dp_w=28, dp_h=24.2)
    _notification_vector(R("app", "src", "main", "res", "drawable", "ic_notification_logo.xml"))
    _bg_vectors()

    # SVG sources
    _mark_svg(R("app", "src", "main", "assets", "Logo.svg"), 560, 484, pad=0.0)
    _mark_svg(R("app", "src", "main", "assets", "LogoTransparent.svg"), 560, 484, pad=0.0)
    _fav = _favicon()
    with open(R("web", "app", "public", "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(_fav)
    print("wrote web/app/public/favicon.svg")
    with open(R("docs", "assets", "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(_fav)
    print("wrote docs/assets/favicon.svg")

    # Master mark, same artwork as the favicon plus the design note.
    master = _fav.replace(
        'fill="none" xmlns="http://www.w3.org/2000/svg">',
        'fill="none" xmlns="http://www.w3.org/2000/svg">\n'
        "<!--\n"
        "  ZMyusic monogram: an interlocked Z + M drawn as one continuous rounded\n"
        "  stroke on the brand squircle. Navy field, cyan->blue gradient ink, same\n"
        "  visual language as the rest of the ZMyusic brand.\n"
        "-->",
        1,
    )
    with open(R("branding", "zmyusic-mark.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(master)
    print("wrote branding/zmyusic-mark.svg")

    # Desktop ICO / ICNS
    write_ico(R("desktopApp", "packaging", "icons", "AppIcon.ico"))
    write_icns(R("desktopApp", "packaging", "icons", "AppIcon.icns"))

    # TV banner (1024x576, TV-safe) and Wear launcher icons
    tv = A.banner(1024, 576)
    for dens in ("", "drawable-hdpi", "drawable-mdpi", "drawable-xhdpi"):
        p = R("tv", "src", "main", "res", dens, "tv_banner.png") if dens else R("tv", "src", "main", "res", "drawable", "tv_banner.png")
        save(tv, p)
    for dens, px in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144)):
        save(A.icon(px), R("wearos", "src", "main", "res", f"mipmap-{dens}", "ic_launcher.png"))

    # iOS preview images (light/dark) for each AppIconPreviews imageset. These
    # only feed the in-app icon picker, so they mirror the shipped icon; the
    # dark variants get the darker navy plate the icon itself uses in dark mode.
    previews = {
        "AppIconPreview": False,
        "AppIconGlassDarkPreview": True,
        "AppIconGlassClearPreview": False,
        "AppIconGlassClearDarkPreview": True,
        "AppIconMonochromePreview": False,
    }
    for name, dark in previews.items():
        base = R("ios", "App", "ZMyusic", "Assets.xcassets", "AppIconPreviews", f"{name}.imageset")
        for variant in ("light", "dark"):
            img = _ios_preview(204, dark=(dark or variant == "dark"), appearance_dark=(variant == "dark"))
            save(img, os.path.join(base, f"{variant}.png"))

    print("done")


if __name__ == "__main__":
    main()
