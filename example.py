import termbuf
import time

# mimick a 0.91" 128x32 monochrome OLED
oled = termbuf.TermBuffer(128, 32)

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
