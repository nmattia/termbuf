# Run with:
# $ podman run --platform linux/amd64 --rm -it -v $PWD:/remote micropython/unix micropython /remote/oled.py

import sys
from binascii import b2a_base64
import framebuf

BPP = 3  # BYTES per pixel


def serialize_gr_command(payload, cmd):
    cmd = ",".join(f"{k}={v}" for k, v in cmd.items())
    ans = []
    w = ans.append
    w(b"\033_G"), w(cmd.encode("ascii"))
    if payload:
        w(b";")
        w(payload)
    w(b"\033\\")
    return b"".join(ans)


# image width & height in pixels
W = 128
H = 32


def display_buf(buf, w, h):
    data = b2a_base64(buf)
    args = {"a": "T", "f": BPP * 8, "s": w, "v": h, "c": 16, "X": 30, "Y": 20}
    BUFSIZE = 16  # kitty accepts max 4096
    while data:
        chunk, data = data[:BUFSIZE], data[BUFSIZE:]
        args.update({"m": 1 if data else 0})  # 0 iff it's the last chunk
        sys.stdout.buffer.write(serialize_gr_command(chunk, args))
        sys.stdout.flush()
        args.clear()  # args must be printed once (except for m)


def display_framebuf(fbuf_buf):
    # buffer holding the image data in RGB (24 = 3 * 8)
    buf = bytearray(W * H * BPP)
    for i in range(0, len(buf) // BPP):
        # convert to row & col
        row = i // W
        col = i % W
        is_edge = row == 0 or row == H - 1 or col == 0 or col == W - 1  # draw a border

        # compute the page (i.e. byte) index
        page_ix = row // 8 * W + col % W

        # figure out if the pixel (bit) is on by indexing into the page
        pixel_on = bool(fbuf_buf[page_ix] & 0b00000001 << row % 8)
        buf[i * BPP + 0] = 255 if not pixel_on and is_edge else 0
        buf[i * BPP + 1] = 255 if is_edge or pixel_on else 0
        buf[i * BPP + 2] = 255 if is_edge or pixel_on else 0

    display_buf(buf, W, H)
    print("\n")


canvas_buffer = bytearray(H // 8 * W)
canvas = framebuf.FrameBuffer(canvas_buffer, W, H, framebuf.MONO_VLSB)

def render():
    display_framebuf(canvas_buffer)

canvas.fill(0)
canvas.text("Roses are red,", 0, 0)
canvas.text("  Violets R blu,", 0, 8)
canvas.text("  I love Kitty,", 0, 16)
canvas.text("  & U will too.", 0, 24)
render()
