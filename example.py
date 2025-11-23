import termbuf
import time


def run():
    # mimick a 0.96" 128x64 monochrome OLED
    oled = termbuf.TermBuffer(128, 64)

    print()
    print("animation starting...")

    lines = (
        "Roses are red,",
        " Violets R blue,",
        "",
        "MicroPython is",
        "    cool,",
        " and U R too! <3",
    )

    oled.fill(0)
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            oled.text(c, x * 8, y * 8)
            oled.show()
            if c != " ":
                time.sleep(0.2)

    print("done!")


if __name__ == "__main__":
    run()
