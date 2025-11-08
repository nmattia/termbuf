# Run with:
# $ podman run --platform linux/amd64 --rm -it -v $PWD:/remote micropython/unix micropython /remote/oled.py

# The ssd1306 driver uses MONO_VLSB. We should focus on this for now.
# https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html#using-a-ssd1306-oled-display

import sys
from binascii import b2a_base64
import framebuf


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
def kitty_gr_display_bitmap(buf, w, h, chunk_size=4096):
    """
    Args:
        chunk_size: chunk size used to transmit the data to kitty. Kitty accepts max 4096. Default: 4096.
    """

    # c/r: number of columns & rows for the image.
    # TODO: Q: how is this different from W/H? A: W/H are in pixels. C/R are term columns/rows.
    # TODO: Q: what does 'r' default to? based on aspect-ratio from w/h?
    n_cols = 32
    data = b2a_base64(buf)
    args = {
        "a": "T",  # action: [T]ransmit and display image
        "C": 1,  # don't move cursor # TODO: not ideal. Should use "animation" instead.
        "f": 24,  # we use kitty's 24bit RGB bitmap support
        # width & height of bitmap, in pixels
        "s": w,
        "v": h,
        # dimension of the printed image
        # (terminal units)
        "c": n_cols,
    }
    while data:
        chunk, data = data[:chunk_size], data[chunk_size:]
        args.update({"m": 1 if data else 0})  # 0 iff it's the last chunk
        kitty_gr_write_cmd(chunk, args)
        # sys.stdout.buffer.write()
        # sys.stdout.flush()
        args.clear()  # args must be printed once (except for m)


class TermFrameBuf(framebuf.FrameBuffer):
    def __init__(self, width, height):
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

    def show(self):
        for pixel_ix in range(0, self.width * self.height):
            # convert to row & col
            row = pixel_ix // self.width
            col = pixel_ix % self.width

            # compute the page (i.e. byte) index
            page_ix = row // 8 * self.width + col % self.width

            # figure out if the pixel (bit) is on by indexing into the page
            pixel_on = bool(self.buffer[page_ix] & 0b00000001 << row % 8)
            if pixel_on:
                # set pixel to cyan
                self.bitmap[pixel_ix * self.BPP + 0] = 000
                self.bitmap[pixel_ix * self.BPP + 1] = 255
                self.bitmap[pixel_ix * self.BPP + 2] = 255

        kitty_gr_display_bitmap(self.bitmap, self.width, self.height)


# mimick a 0.91" 128x32 monochrome OLED
oled = TermFrameBuf(128, 32)

oled.fill(0)
oled.text("Roses are red,", 0, 0)
oled.text("  Violets R blu,", 0, 8)
oled.text("  I love Kitty,", 0, 16)
oled.text("  & U will too.", 0, 24)

oled.show()
