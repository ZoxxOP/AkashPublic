import asyncio
import math
import os
import time

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch

from config import YOUTUBE_IMG_URL

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

OUT_W, OUT_H = 1280, 720
BASE_W, BASE_H = 1536, 864
SS = 2

BRAND = "TeamAnanyaBots"
FONT_PATH = "font.ttf"          # apna regular font (optional)
FONT_BOLD_PATH = "font_bold.ttf"  # apna bold font (optional)

_REG_FALLBACKS = [
    FONT_PATH,
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
_BOLD_FALLBACKS = [
    FONT_BOLD_PATH,
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]

DIRECT_THUMB_FALLBACK = "https://i.ytimg.com/vi/{videoid}/hqdefault.jpg"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in (_BOLD_FALLBACKS if bold else _REG_FALLBACKS):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size)  # Pillow >= 10.1
    except Exception:
        return ImageFont.load_default()


def _fmt(sec: int) -> str:
    sec = max(0, int(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _parse_duration(text) -> int:
    if not text:
        return 0
    try:
        total = 0
        for part in str(text).split(":"):
            total = total * 60 + int(part)
        return total
    except Exception:
        return 0


def _cover(image: Image.Image, w: int, h: int) -> Image.Image:
    ratio = w / h
    if image.width / image.height > ratio:
        nw = int(image.height * ratio)
        left = (image.width - nw) // 2
        image = image.crop((left, 0, left + nw, image.height))
    else:
        nh = int(image.width / ratio)
        top = (image.height - nh) // 2
        image = image.crop((0, top, image.width, top + nh))
    return image.resize((w, h), Image.Resampling.LANCZOS)


def _fit_text(draw, text: str, font, max_w: int) -> str:
    if draw.textlength(text, font=font) <= max_w:
        return text
    while text and draw.textlength(text + "...", font=font) > max_w:
        text = text[:-1]
    return text.rstrip() + "..."


def _star(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def render_card(
    cover: Image.Image,
    title: str,
    channel: str,
    total_sec: int,
    elapsed_sec: int = 0,
    brand: str = BRAND,
) -> Image.Image:
    cover = cover.convert("RGB")

    bg = _cover(cover, BASE_W, BASE_H).filter(ImageFilter.GaussianBlur(10))
    bg = ImageEnhance.Brightness(bg).enhance(0.42)
    bg = ImageEnhance.Color(bg).enhance(1.15)

    card_box = (370, 154, 1166, 710)
    radius = 40

    glass = bg.crop(card_box).filter(ImageFilter.GaussianBlur(14))
    glass = Image.blend(glass, Image.new("RGB", glass.size, (12, 12, 12)), 0.62)
    mask = Image.new("L", (glass.width * SS, glass.height * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, glass.width * SS - 1, glass.height * SS - 1), radius * SS, fill=255
    )
    mask = mask.resize(glass.size, Image.Resampling.LANCZOS)
    base = bg.convert("RGBA")
    base.paste(glass, card_box[:2], mask)

    art_size = 220
    art_pos = (428, 220)
    art = _cover(cover, art_size, art_size).convert("RGBA")
    art_mask = Image.new("L", (art_size * SS, art_size * SS), 0)
    ImageDraw.Draw(art_mask).rounded_rectangle(
        (0, 0, art_size * SS - 1, art_size * SS - 1), 26 * SS, fill=255
    )
    art_mask = art_mask.resize((art_size, art_size), Image.Resampling.LANCZOS)

    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (art_pos[0] - 4, art_pos[1] - 2, art_pos[0] + art_size + 4, art_pos[1] + art_size + 8),
        30,
        fill=(0, 0, 0, 200),
    )
    base = Image.alpha_composite(base, shadow.filter(ImageFilter.GaussianBlur(10)))
    base.paste(art, art_pos, art_mask)

    ov = Image.new("RGBA", (BASE_W * SS, BASE_H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    def s(v):
        return int(round(v * SS))

    def box(x0, y0, x1, y1):
        return (s(x0), s(y0), s(x1), s(y1))

    d.rounded_rectangle(
        box(*card_box), s(radius), outline=(255, 255, 255, 80), width=s(1.5)
    )

    f_brand = _font(s(16), bold=True)
    f_title = _font(s(31), bold=True)
    f_chan = _font(s(23))
    f_time = _font(s(17))

    text_x = 668
    max_w = s(1122 - text_x)
    d.text((s(text_x), s(263)), brand, font=f_brand, fill=(170, 170, 170, 255), anchor="lm")
    d.text(
        (s(text_x), s(308)),
        _fit_text(d, title, f_title, max_w),
        font=f_title,
        fill=(255, 255, 255, 255),
        anchor="lm",
    )
    d.text(
        (s(text_x), s(354)),
        _fit_text(d, channel, f_chan, max_w),
        font=f_chan,
        fill=(235, 235, 235, 255),
        anchor="lm",
    )

    bar_x0, bar_x1, bar_y = 492, 1033, 512
    bar_h = 10
    ratio = 0.0
    if total_sec > 0:
        ratio = min(1.0, max(0.0, elapsed_sec / total_sec))
    d.rounded_rectangle(
        box(bar_x0, bar_y - bar_h / 2, bar_x1, bar_y + bar_h / 2),
        s(bar_h / 2),
        fill=(110, 110, 110, 255),
    )
    if ratio > 0:
        fx = bar_x0 + (bar_x1 - bar_x0) * ratio
        d.rounded_rectangle(
            box(bar_x0, bar_y - bar_h / 2, max(fx, bar_x0 + bar_h), bar_y + bar_h / 2),
            s(bar_h / 2),
            fill=(242, 242, 242, 255),
        )
    d.text((s(428), s(510)), _fmt(elapsed_sec), font=f_time, fill=(240, 240, 240, 255), anchor="lm")
    right = "--:--" if total_sec <= 0 else "\u2212" + _fmt(total_sec - elapsed_sec)
    d.text((s(1122), s(510)), right, font=f_time, fill=(240, 240, 240, 255), anchor="rm")

    icon = (232, 232, 232, 255)
    cy = 578

    d.polygon([(s(x), s(y)) for x, y in _star(453, cy - 1, 25, 10.5)], fill=icon)

    def tri_left(cx_right, w=18, h=20):
        return [
            (s(cx_right), s(cy - h)),
            (s(cx_right), s(cy + h)),
            (s(cx_right - w), s(cy)),
        ]

    def tri_right(cx_left, w=18, h=20):
        return [
            (s(cx_left), s(cy - h)),
            (s(cx_left), s(cy + h)),
            (s(cx_left + w), s(cy)),
        ]

    d.polygon(tri_left(619), fill=icon)
    d.polygon(tri_left(637), fill=icon)
    d.polygon(tri_right(910), fill=icon)
    d.polygon(tri_right(928), fill=icon)

    for bx in (746, 777):
        pw = 13
        white = (250, 250, 250, 255)
        d.ellipse(box(bx, 550, bx + pw, 550 + pw), fill=white)
        d.ellipse(box(bx, 605 - pw, bx + pw, 605), fill=white)
        d.rectangle(box(bx, 550 + pw / 2, bx + pw, 605 - pw / 2), fill=white)

    pod = (205, 205, 205, 255)
    for px in (1066, 1090):
        d.ellipse(box(px - 8, 566, px + 8, 582), fill=pod)
        d.rounded_rectangle(box(px - 3, 576, px + 3, 592), s(3), fill=pod)

    vol_y = 662
    v_x0, v_x1 = 463, 1074
    d.rounded_rectangle(
        box(v_x0, vol_y - bar_h / 2, v_x1, vol_y + bar_h / 2),
        s(bar_h / 2),
        fill=(105, 105, 105, 255),
    )
    d.rounded_rectangle(
        box(v_x0, vol_y - bar_h / 2, v_x0 + (v_x1 - v_x0) * 0.65, vol_y + bar_h / 2),
        s(bar_h / 2),
        fill=(190, 190, 190, 255),
    )

    def speaker(cx, waves):
        col = (160, 160, 160, 255)
        x = cx - 11
        d.rectangle(box(x, vol_y - 6, x + 7, vol_y + 6), fill=col)
        d.polygon(
            [(s(x + 6), s(vol_y - 6)), (s(x + 17), s(vol_y - 14)), (s(x + 17), s(vol_y + 14)), (s(x + 6), s(vol_y + 6))],
            fill=col,
        )
        for i in range(waves):
            r = 8 + i * 7
            d.arc(
                box(x + 17 - r + 4, vol_y - r, x + 17 + r + 4, vol_y + r),
                -45,
                45,
                fill=col,
                width=s(2.5),
            )

    speaker(428, 0)
    speaker(1112, 2)

    ov = ov.resize((BASE_W, BASE_H), Image.Resampling.LANCZOS)
    out = Image.alpha_composite(base, ov).convert("RGB")
    return out.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)


async def _meta_pyyt(videoid: str) -> dict:
    out = {}
    for query in (videoid, f"https://www.youtube.com/watch?v={videoid}"):
        try:
            res = await VideosSearch(query, limit=5).next()
            for data in res.get("result", []):
                if (data.get("id") or data.get("videoId")) != videoid:
                    continue
                out["title"] = (data.get("title") or "").strip()
                channel = data.get("channel") or {}
                if isinstance(channel, dict):
                    out["channel"] = channel.get("name") or ""
                out["duration"] = _parse_duration(data.get("duration"))
                thumbs = data.get("thumbnails") or []
                if thumbs:
                    out["thumb"] = thumbs[0].get("url", "").split("?")[0]
                return out
        except Exception as e:
            print(f"[thumb] py_yt failed ({query[:30]}): {e!r}")
    return out


def _ytdlp_sync(videoid: str) -> dict:
    import yt_dlp  # optional: pip install yt-dlp

    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={videoid}", download=False)
    return {
        "title": (info.get("title") or "").strip(),
        "channel": info.get("channel") or info.get("uploader") or "",
        "duration": int(info.get("duration") or 0),
    }


async def _meta_ytdlp(videoid: str) -> dict:
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _ytdlp_sync, videoid)
    except Exception as e:
        print(f"[thumb] yt-dlp failed: {e!r}")
        return {}


async def _meta_oembed(videoid: str) -> dict:
    url = (
        "https://www.youtube.com/oembed?format=json&url="
        f"https://www.youtube.com/watch?v={videoid}"
    )
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    return {
                        "title": (data.get("title") or "").strip(),
                        "channel": data.get("author_name") or "",
                    }
    except Exception as e:
        print(f"[thumb] oembed failed: {e!r}")
    return {}


async def _fetch_meta(videoid: str) -> dict:
    meta = {"title": "", "channel": "", "duration": 0, "thumb": None}

    def merge(new: dict):
        for k, v in (new or {}).items():
            if v and not meta.get(k):
                meta[k] = v

    merge(await _meta_pyyt(videoid))
    if not (meta["title"] and meta["channel"] and meta["duration"]):
        merge(await _meta_ytdlp(videoid))  # song ki duration bhi yahin se aati hai
    if not (meta["title"] and meta["channel"]):
        merge(await _meta_oembed(videoid))
    return meta


async def get_thumb(
    videoid: str,
    progress_percent: int = 0,
    use_cache: bool = True,
    user_name: str = "Akash",
    duration_sec: int = 0,
    played_sec: int = None,
    title: str = None,
    channel: str = None,
) -> str:
    """
    duration_sec / played_sec / title / channel optional hain.
    Bot ke paas song ka data pehle se ho to wahi pass karo (sabse reliable),
    warna YouTube se nikala jayega.
    played_sec do to wahi "kitna chal gaya" dikhega, nahi to progress_percent se nikalega.
    """
    progress_percent = max(0, min(100, int(progress_percent or 0)))
    tag = f"{progress_percent}" if played_sec is None else f"s{int(played_sec)}"
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_glass_{tag}.png")

    if use_cache and os.path.exists(cache_path):
        return cache_path

    thumb_path = os.path.join(CACHE_DIR, f"thumb_{videoid}_{int(time.time())}.jpg")

    try:
        meta = {"title": "", "channel": "", "duration": 0, "thumb": None}
        if not (title and channel and duration_sec):
            meta = await _fetch_meta(videoid)
        meta["title"] = title or meta["title"] or "Unknown Title"
        meta["channel"] = channel or meta["channel"] or "Unknown Channel"
        meta["duration"] = int(duration_sec or meta["duration"] or 0)

        urls = [u for u in (meta["thumb"], DIRECT_THUMB_FALLBACK.format(videoid=videoid)) if u]

        downloaded = False
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for url in urls:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            async with aiofiles.open(thumb_path, "wb") as f:
                                await f.write(data)
                            downloaded = True
                            break
                except Exception:
                    continue

        if not downloaded:
            return YOUTUBE_IMG_URL

        cover = Image.open(thumb_path).convert("RGB")
        total = meta["duration"]
        if played_sec is not None:
            elapsed = int(played_sec)
        else:
            elapsed = int(total * progress_percent / 100) if total else 0
        if total:
            elapsed = min(elapsed, total)

        card = render_card(cover, meta["title"], meta["channel"], total, elapsed)

        complete = meta["title"] != "Unknown Title" and total > 0
        if complete:  # adhoore data wali image cache nahi hogi, next baar dobara try hoga
            card.save(cache_path, "PNG", optimize=True)
            return cache_path
        out = os.path.join(CACHE_DIR, f"{videoid}_glass_tmp.png")
        card.save(out, "PNG", optimize=True)
        return out

    except Exception as e:
        import traceback

        print(f"Thumbnail Error: {e}")
        traceback.print_exc()
        return YOUTUBE_IMG_URL

    finally:
        try:
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        except Exception:
            pass


async def gen_thumb(
    videoid: str,
    progress_percent: int = 0,
    use_cache: bool = True,
    user_name: str = "Akash",
    duration_sec: int = 0,
    played_sec: int = None,
    title: str = None,
    channel: str = None,
) -> str:
    return await get_thumb(
        videoid=videoid,
        progress_percent=progress_percent,
        use_cache=use_cache,
        user_name=user_name,
        duration_sec=duration_sec,
        played_sec=played_sec,
        title=title,
        channel=channel,
    )
    
