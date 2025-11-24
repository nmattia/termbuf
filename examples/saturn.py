import termbuf


def draw_saturn(fbuf, width, height):
    fbuf.line(0, height - 1, width - 1, 0, 1)
    r = min(width, height) // 4
    fbuf.ellipse(width // 2, height // 2, r, r, 1)
    fbuf.show()


def run():
    # mimic a 0.96" 128x64 monochrome OLED
    w, h = 128, 64
    display = termbuf.TermBuffer(w, h)
    draw_saturn(display, w, h)


if __name__ == "__main__":
    run()
    print()
