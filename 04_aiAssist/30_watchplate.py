import time, math
from hw import LCD

# ------------------------------------------------------------
# Color sets (same structure as 028_watchClass.py)
#   color[colorSet][0] = background
#   color[colorSet][1] = hour hand / hour ticks
#   color[colorSet][2] = minute hand / minute ticks
#   color[colorSet][3] = second hand / accents
# ------------------------------------------------------------
color = [
    [LCD.color(  0,  0,  0), LCD.color(220,220,220), LCD.color(160,160,160), LCD.color(255,  0,  0)],
    [LCD.color( 10, 20, 50), LCD.color( 40, 60,120), LCD.color( 90,110,160), LCD.color(255,140,  0)],
    [LCD.color( 10, 30, 20), LCD.color( 30, 80, 60), LCD.color( 70,130,110), LCD.color(220,255,  0)],
    [LCD.color( 30, 10, 40), LCD.color( 80, 40,100), LCD.color(140,100,160), LCD.color(255, 60,150)],
    [LCD.color( 40, 25, 10), LCD.color(100, 70, 40), LCD.color(170,150,110), LCD.color(220, 30, 30)],
    [LCD.color( 20, 20, 20), LCD.color( 60, 60, 60), LCD.color(150,150,150), LCD.color(  0,200,255)],
    [LCD.color(  5, 30, 35), LCD.color( 20, 80, 90), LCD.color( 60,130,160), LCD.color(255,220,  0)],
    [LCD.color( 40, 10, 15), LCD.color(120, 40, 50), LCD.color(190,120,120), LCD.color(255, 80,  0)],
    [LCD.color(  5, 15, 40), LCD.color( 30, 50,100), LCD.color( 80,110,160), LCD.color(  0,255,120)],
    [LCD.color( 25, 20, 35), LCD.color( 70, 60, 90), LCD.color(140,130,160), LCD.color(  0,220,200)],
    [LCD.color( 35, 20, 10), LCD.color( 90, 60, 30), LCD.color(190,160,120), LCD.color(255, 40, 40)],
    [LCD.color(  0,  5, 15), LCD.color( 10, 20, 40), LCD.color(120,130,150), LCD.color( 50,180,255)]
]


class Watch:
    """Watch face with tick marks + triangular hour/minute hands.

    This file is adapted to match 028_watchClass.py structure:
    - uses `from hw import LCD`
    - defines a `Watch` class with `draw()`
    - optional bottom loop for standalone running
    """

    def __init__(self, cx, cy, factor, colorSet):
        self.cx = cx
        self.cy = cy
        self.factor = factor
        self.colorSet = colorSet

        # Base radius: keep consistent with 028 (factor * 120)
        self.r = self.factor * 120

        # Plate geometry (scaled from original 029: platesize=40, hour tick=34, minute tick=38)
        self.platesize   = self.r
        self.tickmark_h  = self.platesize * 0.85
        self.tickmark_m  = self.platesize * 0.95

        # Hands (scaled from original 029)
        self.hour_len = self.platesize * 0.50
        self.min_len  = self.platesize * 0.80
        self.sec_len  = self.platesize * 0.90

        # Base widths for triangle hands
        self.hour_base = max(2, int(self.platesize * 0.10))
        self.min_base  = max(2, int(self.platesize * 0.075))

        self._plate_drawn = False

    # -------------------------
    # Static dial (draw once)
    # -------------------------
    def _draw_plate(self):
        bg = color[self.colorSet][0]
        c_h = color[self.colorSet][1]
        c_m = color[self.colorSet][2]

        LCD.fill(bg)

        # minute ticks
        for i in range(60):
            ang = math.radians(6 * i)
            LCD.line(
                self.cx + int(self.tickmark_m * math.sin(ang)),
                self.cy - int(self.tickmark_m * math.cos(ang)),
                self.cx + int(self.platesize  * math.sin(ang)),
                self.cy - int(self.platesize  * math.cos(ang)),
                c_m
            )

        # hour ticks
        for i in range(12):
            ang = math.radians(30 * i)
            LCD.line(
                self.cx + int(self.tickmark_h * math.sin(ang)),
                self.cy - int(self.tickmark_h * math.cos(ang)),
                self.cx + int(self.platesize  * math.sin(ang)),
                self.cy - int(self.platesize  * math.cos(ang)),
                c_h
            )

        self._plate_drawn = True

    # -------------------------
    # Triangular hand helper
    # -------------------------
    def _spin_tri(self, angle_deg, base_w, length, c):
        # base_w: half-width (pixels)
        bx = int(base_w * math.sin(math.radians(angle_deg + 90)))
        by = int(base_w * math.cos(math.radians(angle_deg + 90)))
        tx = int(length * math.sin(math.radians(angle_deg)))
        ty = int(length * math.cos(math.radians(angle_deg)))

        # LCD.fill_tri is implemented in touch.py (resident in /lib on device)
        LCD.fill_tri(
            self.cx + tx, self.cy - ty,
            self.cx + bx, self.cy - by,
            self.cx - bx, self.cy + by,
            c
        )

    # -------------------------
    # Frame update (once/sec)
    # -------------------------
    def draw(self):
        if not self._plate_drawn:
            self._draw_plate()

        now = time.localtime()
        h = now[3] % 12

        # Angles in degrees
        hour_ang = 30 * h + 0.5 * now[4]
        min_ang  = 6 * now[4] + 0.1 * now[5]
        sec_ang  = 6 * now[5]

        bg = color[self.colorSet][0]
        c_h = color[self.colorSet][1]
        c_m = color[self.colorSet][2]
        c_s = color[self.colorSet][3]

        # Draw hands
        self._spin_tri(hour_ang, self.hour_base, self.hour_len, c_h)
        self._spin_tri(min_ang,  self.min_base,  self.min_len,  c_m)

        sx = int(self.sec_len * math.sin(math.radians(sec_ang)))
        sy = int(self.sec_len * math.cos(math.radians(sec_ang)))
        LCD.line(self.cx, self.cy, self.cx + sx, self.cy - sy, c_s)

        LCD.show()

        # Erase hands only
        self._spin_tri(hour_ang, self.hour_base, self.hour_len, bg)
        self._spin_tri(min_ang,  self.min_base,  self.min_len,  bg)
        LCD.line(self.cx, self.cy, self.cx + sx, self.cy - sy, bg)


# Standalone run (same pattern as 028_watchClass.py)
watch = Watch(70, 70, 0.35, 7)

while True:
    watch.draw()
    time.sleep(1)
