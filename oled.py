# Run with:
# $ podman run --platform linux/amd64 --rm -it -v $PWD:/remote micropython/unix micropython /remote/oled.py

# The ssd1306 driver uses MONO_VLSB. We should focus on this for now.
# https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html#using-a-ssd1306-oled-display

import sys
from binascii import b2a_base64
import framebuf
import random
import time


# write a kitty graphics protocol command to stdout
def kitty_gr_write_cmd(payload, cmd):
    cmd = ",".join(f"{k}={v}" for k, v in cmd.items())
    for cmd in (
        b"\033_G",
        cmd.encode("ascii"),
        b";",
        payload,
        b"\033\\",
    ):
        sys.stdout.buffer.write(cmd)

    sys.stdout.flush()


# display a bitmap (24bit RGB) data to the terminal.
def kgp_image_transmit(buf, w, h, image_id, chunk_size=4096):
    """
    Args:
        image_id: id that will be used when referring to (updating) the image
        chunk_size: chunk size used to transmit the data to kitty. Kitty accepts max 4096. Default: 4096.
    """

    data = b2a_base64(buf)
    args = {
        "a": "T",  # action: [T]ransmit and display image
        "f": 24,  # we use kitty's 24bit RGB bitmap support
        "i": image_id,  # id that we might/will use later to update the image
        # width & height of bitmap, in pixels
        "s": w,
        "v": h,
        # dimension of the printed image
        # (terminal units)
        "c": 32,  # term columns, somewhat arbitrary. [r]ows are inferred from aspect ratio.
        "q": 1,  # suppress terminal responses
    }
    while data:
        chunk, data = data[:chunk_size], data[chunk_size:]
        args.update({"m": 1 if data else 0})  # 0 iff it's the last chunk
        kitty_gr_write_cmd(chunk, args)
        args.clear()  # args must be printed once (except for m)


# display a bitmap (24bit RGB) data to the terminal.
def kgp_image_frame(buf, w, h, image_id, chunk_size=4096):
    """
    Args:
        image_id: id of the image to update
        chunk_size: chunk size used to transmit the data to kitty. Kitty accepts max 4096. Default: 4096.
    """

    data = b2a_base64(buf)
    args = {
        "a": "f",  # action: send a display a [f]rame
        "f": 24,  # we use kitty's 24bit RGB bitmap support
        "i": image_id,  # which image to update
        # width & height of bitmap, in pixels
        "s": w,
        "v": h,
        "q": 1,  # suppress terminal responses
    }
    while data:
        chunk, data = data[:chunk_size], data[chunk_size:]
        args.update({"m": 1 if data else 0})  # 0 iff it's the last chunk
        kitty_gr_write_cmd(chunk, args)
        args.clear()  # args must be printed once (except for m)


class TermBuffer(framebuf.FrameBuffer):
    def __init__(self, width, height):
        """Creates a kitty graphics protocol image that can be updated with .show().

        Note: the image is never deleted.
        """

        # width & height in (monochrome) pixels
        self.width = width
        self.height = height

        # buffer used by framebuf
        # 1 byte = 8 vertical pixels
        # 1 page = 1 column
        # https://docs.micropython.org/en/latest/library/framebuf.html#framebuf.framebuf.MONO_VLSB
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)

        # bitmap we'll eventually render to
        self.BPP = 3  # bytes per pixels in bitmap (one for R, one for G, one for B)
        self.bitmap = bytearray(self.width * self.height * self.BPP)

        # random id to avoid collisions with other potential images, see [i]:
        # https://sw.kovidgoyal.net/kitty/graphics-protocol/#control-data-reference
        self.image_id = random.randint(0, 4294967294)

        # create an empty image (will already allocate space in term)
        kgp_image_transmit(self.bitmap, self.width, self.height, image_id=self.image_id)

    def show(self):
        for pixel_ix in range(0, self.width * self.height):
            # convert to row & col
            row = pixel_ix // self.width
            col = pixel_ix % self.width

            # compute the page (i.e. byte) index
            page_ix = row // 8 * self.width + col % self.width

            # figure out if the pixel (bit) is on by indexing into the page
            pixel_on = bool(self.buffer[page_ix] & 0b00000001 << row % 8)

            c = [0, 255, 255] if pixel_on else [0, 0, 0]
            # set pixel color
            # NOTE: micropython does not support range assignment
            self.bitmap[pixel_ix * self.BPP + 0] = c[0]
            self.bitmap[pixel_ix * self.BPP + 1] = c[1]
            self.bitmap[pixel_ix * self.BPP + 2] = c[2]

        kgp_image_frame(self.bitmap, self.width, self.height, image_id=self.image_id)


# mimick a 0.91" 128x32 monochrome OLED
oled = TermBuffer(128, 32)

print()
print("oled ready", end="")

i = 0
while True:
    time.sleep(1)
    oled.fill(0)
    oled.text("Roses are red,", 0, 0)
    oled.text("  Violets R blu,", 0, 8)
    oled.text("  I love Kitty,", 0, 16)
    oled.text(f"{i} & U will too.", 0, 24)
    oled.show()
    print(".", end="")
    i = i + 1
