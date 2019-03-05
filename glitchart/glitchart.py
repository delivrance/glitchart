# MIT License
#
# Copyright (c) 2019 Dan Tès <https://github.com/delivrance>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import logging
import os
import subprocess
from pathlib import Path
from random import Random
from uuid import uuid4

from PIL import Image

MIN_AMOUNT_IMAGE = 1
MAX_AMOUNT_IMAGE = 10

MIN_AMOUNT_VIDEO = 0
MAX_AMOUNT_VIDEO = 3

MIN_SEED = -2 ** 63
MAX_SEED = 2 ** 63 - 1

SOS = b"\xFF\xDA"  # Start Of Scan
EOI = b"\xFF\xD9"  # End Of Image

OUT_NAME_TEMPLATE = "{}_glitch.{}"

log = logging.getLogger(__name__)


def jpeg(photo: str,
         seed: int = None,
         min_amount: int = MIN_AMOUNT_IMAGE,
         max_amount: int = MAX_AMOUNT_IMAGE,
         inplace: bool = False) -> str:
    """Glitch a JPEG file. A new image will be saved in the current working directory with the string
    "_glitch" appended to the filename. E.g.: "monalisa.jpg" becomes "monalisa_glitch.jpg".

    Args:
        photo (str):
            JPEG photo file to glitch.
            Pass a file path as string to glitch a photo that exists on your local machine.

        seed (int, optional):
            Pseudo-random number generator seed.
            Using again the same seed on the original file will result in identical glitched images.
            Defaults to a random value.

        min_amount (int, optional):
            Minimum amount of bytes to corrupt.
            A negative value will result in min_amount = 0.
            A value higher than max_amount will result in max_amount = min_amount.
            The actual amount will be chosen randomly in range [min_amount, max_amount].
            Defaults to 1.

        max_amount (int, optional):
            Maximum amount of bytes to corrupt.
            A negative value will result in max_amount = 1.
            A value lower than min_amount will result in max_amount = min_amount.
            The actual amount will be chosen randomly in range [min_amount, max_amount].
            Defaults to 10.

        inplace (bool, optional):
            Pass True to glitch the image in-place and avoid creating a new JPEG file.
            This will overwrite the original image.
            Defaults to False.

    Returns:
        On success, the absolute path of the glitched image is returned.
    """
    out = photo if inplace else OUT_NAME_TEMPLATE.format(Path(photo).stem, "jpg")
    prng = Random(seed)

    if min_amount < 0:
        min_amount = 0

    if max_amount < 0:
        max_amount = 1

    if min_amount > max_amount:
        max_amount = min_amount

    amount = prng.randint(min_amount, max_amount)

    with open(photo, "rb") as f:
        original = f.read()

        start = original.index(SOS) + len(SOS) + 10
        end = original.rindex(EOI)

        data = bytearray(original[start:end])
        glitched = set()

        for _ in range(amount):
            while True:
                index = prng.randrange(len(data))

                if index not in glitched:
                    if data[index] not in [0, 255]:
                        glitched.add(index)
                        break

            while True:
                value = prng.randint(1, 254)

                if data[index] != value:
                    data[index] = value
                    break

    with open(out, "wb") as f:
        f.write(
            original[:start]
            + data
            + original[end:]
        )

    return Path(out).absolute()


async def jpeg_async(*args, **kwargs):
    return jpeg(*args, **kwargs)


def png(photo: str,
        seed: int = None,
        min_amount: int = MIN_AMOUNT_IMAGE,
        max_amount: int = MAX_AMOUNT_IMAGE,
        inplace: bool = False):
    out = photo if inplace else OUT_NAME_TEMPLATE.format(Path(photo).stem, "png")
    jpg_path = "{}.jpg".format(uuid4())

    png = Image.open(photo).convert("RGBA")

    bg = Image.new("RGB", png.size, (255, 255, 255))
    bg.paste(png, png)
    bg.save(jpg_path)

    jpeg(jpg_path, seed, min_amount, max_amount, True)

    Image.open(jpg_path).convert("RGBA").save(out)

    os.remove(jpg_path)

    return Path(out).absolute()


async def png_async(*args, **kwargs):
    return png(*args, **kwargs)


def webp(photo: str,
         seed: int = None,
         min_amount: int = MIN_AMOUNT_IMAGE,
         max_amount: int = MAX_AMOUNT_IMAGE,
         inplace: bool = False):
    out = photo if inplace else OUT_NAME_TEMPLATE.format(Path(photo).stem, "webp")
    png_path = "{}.png".format(uuid4())

    webp = Image.open(photo)
    webp.save(png_path)

    png(png_path, seed, min_amount, max_amount, True)

    Image.open(png_path).save(out)

    os.remove(png_path)

    return Path(out).absolute()


async def webp_async(*args, **kwargs):
    return webp(*args, **kwargs)


def mp4(video: str,
        seed: int = None,
        min_amount: int = MIN_AMOUNT_VIDEO,
        max_amount: int = MAX_AMOUNT_VIDEO,
        inplace: bool = False):
    out = video if inplace else OUT_NAME_TEMPLATE.format(Path(video).stem, "mp4")
    uuid = uuid4()

    try:
        fps = subprocess.check_output(
            "ffprobe -v error -select_streams v -of "
            "default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate {video}".format(
                video=video
            ),
            shell=True
        ).strip().decode()

        os.system(
            "ffmpeg -loglevel quiet -i {video} {uuid}_%8d.jpg".format(
                video=video,
                uuid=uuid
            )
        )

        prng = Random(seed)

        for p in sorted(Path().rglob(f"{uuid}_*.jpg")):
            jpeg(str(p), prng.getrandbits(2500), min_amount, max_amount, inplace=True)

        os.system(
            "ffmpeg -loglevel quiet -r {fps} -i {uuid}_%8d.jpg {out} -y".format(
                fps=fps,
                uuid=uuid,
                out=out
            )
        )
    except Exception as e:
        log.error(e)
    finally:
        for p in Path().rglob(f"{uuid}_*.jpg"):
            try:
                os.remove(str(p))
            except OSError:
                pass

    return Path(out).absolute()


async def mp4_async(video: str,
                    seed: int = None,
                    min_amount: int = MIN_AMOUNT_VIDEO,
                    max_amount: int = MAX_AMOUNT_VIDEO,
                    inplace: bool = False):
    out = video if inplace else OUT_NAME_TEMPLATE.format(Path(video).stem, "mp4")
    uuid = uuid4()

    try:
        fps = subprocess.check_output(
            "ffprobe -v error -select_streams v -of "
            "default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate {video}".format(
                video=video
            ),
            shell=True
        ).strip().decode()

        process = await asyncio.create_subprocess_shell(
            "ffmpeg -loglevel quiet -i {video} {uuid}_%8d.jpg".format(
                video=video,
                uuid=uuid
            )
        )
        await process.wait()

        prng = Random(seed)

        for p in sorted(Path().rglob(f"{uuid}_*.jpg")):
            jpeg(str(p), prng.randint(MIN_SEED, MAX_SEED), min_amount, max_amount, inplace=True)

        process = await asyncio.create_subprocess_shell(
            "ffmpeg -loglevel quiet -r {fps} -i {uuid}_%8d.jpg {out} -y".format(
                fps=fps,
                uuid=uuid,
                out=out
            )
        )
        await process.wait()
    except Exception as e:
        log.error(e)
    finally:
        for p in Path().rglob("{uuid}_*.jpg".format(uuid=uuid)):
            try:
                os.remove(str(p))
            except OSError:
                pass

    return Path(out).absolute()
