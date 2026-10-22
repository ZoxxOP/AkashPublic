import os
import time
import aiofiles
import aiohttp

from PIL import Image, ImageEnhance
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL


CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

WIDTH = 1280
HEIGHT = 720

DIRECT_THUMB_FALLBACK = "https://i.ytimg.com/vi/{videoid}/hqdefault.jpg"


async def _fetch_meta_via_search(videoid: str):
    for _attempt in range(2):
        try:
            results = VideosSearch(
                f"https://www.youtube.com/watch?v={videoid}",
                limit=1,
            )

            results_data = await results.next()
            data = results_data.get("result", [{}])[0]

            fetched_id = data.get("id") or data.get("videoId")

            if fetched_id and fetched_id != videoid:
                continue

            thumbnails = data.get("thumbnails", [])
            thumbnail_url = ""

            if thumbnails:
                thumbnail_url = thumbnails[0].get("url", "").split("?")[0]

            if thumbnail_url:
                return thumbnail_url

        except Exception:
            pass

    return None


async def get_thumb(
    videoid: str,
    progress_percent: int = 0,
    use_cache: bool = True,
    user_name: str = "Akash",
) -> str:

    print(
        f"get_thumb called with videoid: {videoid}, "
        f"progress: {progress_percent}%"
    )

    cache_path = os.path.join(
        CACHE_DIR,
        f"{videoid}_normal.png",
    )

    if use_cache and os.path.exists(cache_path):
        return cache_path

    thumb_path = os.path.join(
        CACHE_DIR,
        f"thumb_{videoid}_{int(time.time())}.jpg",
    )

    thumbnail_url = await _fetch_meta_via_search(videoid)

    if not thumbnail_url:
        thumbnail_url = DIRECT_THUMB_FALLBACK.format(
            videoid=videoid
        )

    downloaded = False

    urls = (
        thumbnail_url,
        DIRECT_THUMB_FALLBACK.format(videoid=videoid),
    )

    try:
        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            for url in urls:
                try:
                    async with session.get(url) as resp:

                        if resp.status == 200:
                            data = await resp.read()

                            async with aiofiles.open(
                                thumb_path,
                                "wb",
                            ) as f:
                                await f.write(data)

                            downloaded = True
                            break

                except Exception:
                    continue

        if not downloaded:
            return YOUTUBE_IMG_URL

        image = Image.open(thumb_path).convert("RGB")

        source_ratio = image.width / image.height
        target_ratio = WIDTH / HEIGHT

        if source_ratio > target_ratio:
            new_width = int(
                image.height * target_ratio
            )

            left = (
                image.width - new_width
            ) // 2

            image = image.crop(
                (
                    left,
                    0,
                    left + new_width,
                    image.height,
                )
            )

        elif source_ratio < target_ratio:
            new_height = int(
                image.width / target_ratio
            )

            top = (
                image.height - new_height
            ) // 2

            image = image.crop(
                (
                    0,
                    top,
                    image.width,
                    top + new_height,
                )
            )

        image = image.resize(
            (WIDTH, HEIGHT),
            Image.Resampling.LANCZOS,
        )

        image = ImageEnhance.Color(
            image
        ).enhance(1.03)

        image = ImageEnhance.Contrast(
            image
        ).enhance(1.02)

        image.save(
            cache_path,
            "PNG",
            optimize=True,
        )

        print(
            f"Normal thumbnail saved: {cache_path}"
        )

        return cache_path

    except Exception as e:
        import traceback

        print(
            f"Thumbnail Error: {e}"
        )

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
) -> str:

    return await get_thumb(
        videoid=videoid,
        progress_percent=progress_percent,
        use_cache=use_cache,
        user_name=user_name,
            )
