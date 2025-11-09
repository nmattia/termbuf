# termbuf

MicroPython library for displaying OLED graphics in the terminal using the Kitty Graphics Protocol.

The library provides the same interface as eg the [`ssd1306` micropython driver](https://github.com/stlehmann/micropython-ssd1306), meaning the same code can be used in both to output to the terminal or to a real OLED display.

See [Getting Started](#getting-started) for a quick introduction and see the [examples](#examples) below for some real-world use cases.

## Getting Started

Start a MicroPython REPL. If you have a MicroPython device connected this is done by calling `mpremote`. You can also start MicroPython in a container:

```bash
docker run --rm -it micropython/unix
```

Then, install `termbuf`:

```python
import mip
mip.install("github:nmattia/termbuf")
```

You can then display OLED data in your terminal (you can use `Ctrl+E` to enter MicroPython "paste mode"):

```python
import termbuf

# mimick a 0.91" 128x32 monochrome OLED
oled = termbuf.TermBuffer(128, 32)

oled.fill(0)
oled.text("hello, world", 0, 8)
oled.show()
print() # move the cursor down if necessary
```

![Screenshot of an emulated OLED display showing the text "hello, world"](./docs/images/hello-world.png)

> [!NOTE]
>
> The `termbuf` library makes use of the [Terminal Graphics Protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/) implemented by terminals like [kitty](https://github.com/kovidgoyal/kitty) and [ghostty](https://ghostty.org). If you do not see an image, your terminal might not support the Terminal Graphics Protocol.

The full [`framebuf`](https://docs.micropython.org/en/latest/library/framebuf.html) API is available. You can edit the contents at will and update the display by calling `show()`:

```python
oled.text("yoo-hoo", 0, 16)
oled.show()
```

![Screenshot of an emulated OLED display showing the text "hello, world" and "yoo-hoo"](./docs/images/hello-world-yoo-hoo.png)

## Examples

There are some examples that you can copy/paste to a MicroPython REPL. These assume you have installed `termbuf` with `mpremote mip install github:nmattia/termbuf` or from within MicroPython with `import mip` and `mip.install("github:nmattia/termbuf")`.

### Animation

The terminal image objects created with `termbuf` can be updated.

```python
import termbuf
import time

# mimick a 128x64 OLED
oled = termbuf.TermBuffer(128, 64)

d = 0
while True:
    oled.fill(0)
    d = d + 5
    d = d % 40
    oled.fill_rect(10, 20, 20 + d, 20, 1)
    oled.show()
    time.sleep(1)
```

![Progress bar in a terminal.](./docs/images/progress-bar.mov)

### Determining which driver to use

It is possible to use a different driver (eg actual I2C OLED vs terminal) depending on the port:

```python
import termbuf
import sys

W = 128
H = 32

if sys.platform == 'linux':
    # if this is the unix port, use `termbuf`
    oled = termbuf.TermBuffer(W, H)
else:
    # otherwise, use the physical OLED via i2c
    from ssd1306 import SSD1306_I2C
    from machine import Pin, I2C
    i2c = I2C(1, scl=Pin(7, Pin.OUT), sda=Pin(6, Pin.OUT), freq=400000)
    oled = SSD1306_I2C(128, 32, i2c)

oled.fill(0)
oled.text("hello, world", 0, 8)
oled.show()
```
