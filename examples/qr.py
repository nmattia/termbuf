# this requires uqr to be installed:
#
# >>> import mip
# >>> mip.install('https://raw.githubusercontent.com/JASchilz/uQR/c1ffdc94aae8bcd46aa8908b7f7a291e049f95b4/uQR.py')

import termbuf

import uQR
from uQR import QRCode


def run():
    # here we add some options to make the QR code smaller
    qr = QRCode(border=0, error_correction=uQR.ERROR_CORRECT_L)
    qr.add_data("https://github.com/nmattia/termbuf")
    matrix = qr.get_matrix()

    scaling = 4  # scaling factor because some terminals do antialiasing
    display = termbuf.TermBuffer(32 * scaling, 32 * scaling)

    # Adapted from uQR README:
    # https://github.com/JASchilz/uQR
    for y in range(len(matrix) * scaling):
        for x in range(len(matrix[0]) * scaling):
            value = not matrix[y // scaling][x // scaling]
            display.pixel(x, y, value)

    display.show()


if __name__ == "__main__":
    run()
