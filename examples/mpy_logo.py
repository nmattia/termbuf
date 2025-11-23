import termbuf


def run():
    dim = 256
    wide = (dim * 11) // 50
    narrow = (dim * 2) // 50
    eye_pad_right = (dim * 4) // 50
    eye_pad_bottom = (dim * 5) // 50
    eye_width = (dim * 2) // 50
    eye_height = (dim * 4) // 50

    display = termbuf.TermBuffer(256, 256)

    for i in range(0, 4):
        for y in range(0, dim):
            display.rect(i * (wide + narrow), y, wide, 1, 1, True)
    for i in range(0, 3):
        y = 0 if i % 2 == 0 else dim - wide
        display.rect(wide + i * (narrow + wide), y, narrow, wide, 1, True)

    display.rect(
        dim - eye_pad_right - eye_width,
        dim - eye_pad_bottom - eye_height,
        eye_width,
        eye_height,
        0,
        True,
    )

    display.show()


if __name__ == "__main__":
    run()
