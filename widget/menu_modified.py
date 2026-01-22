# 調整長按時間 到 line 219 1200ms --> 2000 ms 長按兩秒

import os, time, math, gc
import touch
import hw

# -------------------------
# LCD / 觸控 / IMU 由 hw.py 統一初始化
# （menu 不再自行 new LCD/TP，以避免重複初始化與記憶體浪費）
# -------------------------
LCD = hw.LCD
TP  = getattr(hw, "TP", None)
IMU = getattr(hw, "IMU", None)

W, H = 240, 240
CX, CY = 120, 120

# 顏色（沿用你 driver 的 color()）
c_bg   = LCD.color(0, 0, 0)
c_ring = LCD.color(40, 40, 40)
c_txt  = LCD.color(230, 230, 230)
c_dim  = LCD.color(130, 130, 130)
c_sel  = LCD.color(0, 220, 160)
c_err  = LCD.color(255, 80, 80)

R_OUT  = 118
R_IN   = 78
R_ICON = 14

EXCLUDE = set(["boot.py", "main.py", "touch.py", "menu.py"])


# 由 TouchAdapter 於初始化時設定；供 run_script 長按退回監控使用
TP_SINGLETON = TP
# -------------------------
# 小工具
# -------------------------
def clamp(v, a, b):
    return a if v < a else (b if v > b else v)

def safe_clear():
    LCD.fill(c_bg)

def draw_center_lines(lines, color=c_txt, y0=None):
    # 使用 LCD.text()；字寬約 8px
    if y0 is None:
        y0 = CY - (len(lines) * 10) // 2
    y = y0
    for s in lines:
        x = CX - (len(s) * 8) // 2
        LCD.text(s, x, y, color)
        y += 12

def draw_circle_outline(cx, cy, r, col):
    # Midpoint circle (outline)
    x = r
    y = 0
    d = 1 - r
    while x >= y:
        LCD.pixel(cx + x, cy + y, col)
        LCD.pixel(cx + y, cy + x, col)
        LCD.pixel(cx - y, cy + x, col)
        LCD.pixel(cx - x, cy + y, col)
        LCD.pixel(cx - x, cy - y, col)
        LCD.pixel(cx - y, cy - x, col)
        LCD.pixel(cx + y, cy - x, col)
        LCD.pixel(cx + x, cy - y, col)
        y += 1
        if d < 0:
            d += 2 * y + 1
        else:
            x -= 1
            d += 2 * (y - x) + 1

def fill_circle(cx, cy, r, col):
    # 小半徑填滿圓（r<=16 用簡單掃描足夠快）
    rr = r * r
    for dy in range(-r, r + 1):
        y = cy + dy
        if y < 0 or y >= H:
            continue
        dx_max = int((rr - dy * dy) ** 0.5)
        x0 = cx - dx_max
        x1 = cx + dx_max
        if x0 < 0: x0 = 0
        if x1 >= W: x1 = W - 1
        LCD.hline(x0, y, x1 - x0 + 1, col)

def list_py_files():
    files = []
    try:
        for fn in os.listdir():
            if not fn.endswith(".py"):
                continue
            if fn in EXCLUDE or fn.startswith("."):
                continue
            # 排除目錄（有些韌體 os.stat 回傳 tuple）
            try:
                st = os.stat(fn)
                # MicroPython：st[0] 可能是 mode；bit 檢查在不同 port 不一樣，保守處理
                # 若 stat 失敗或不可判斷，就仍加入
            except Exception:
                pass
            files.append(fn)
    except Exception:
        pass
    files.sort()
    return files

def _free_memory_before_run(keep_modules=("sys","gc","os","time","math","touch","hw")):
    import sys, gc

    # 1) 先做一次 GC
    gc.collect()

    # 2) 卸載大多數已載入模組（避免佔 RAM）
    #    只保留：系統核心 + 你的 touch/LCD（否則 Menu 畫面會炸）
    for k in list(sys.modules.keys()):
        if k in keep_modules:
            continue
        # micropython 內建的一些底層模組也可保留，避免奇怪問題
        if k.startswith("micropython") or k.startswith("u"):
            continue
        try:
            del sys.modules[k]
        except Exception:
            pass

    # 3) 再 GC 一次
    gc.collect()

    # 4) 若你的韌體支援 heap_info，可用來觀察（可留可刪）
    try:
        import micropython
        micropython.mem_info()
    except Exception:
        pass



# -------------------------
# 子程式返回 Menu（長按）
# -------------------------
class AbortToMenu(Exception):
    """Raised internally to abort a running script and return to menu."""
    pass

class LongPressGuard:
    """
    在「子程式執行期間」監控長按，觸發則丟 AbortToMenu。
    由於你的 touch.py 在 Mode=1 時只有 IRQ 才更新座標，
    這裡採用 I2C 直接輪詢座標暫存（0x03..0x06）來判斷是否仍在按壓，
    可在不改子程式碼的前提下提供較穩定的長按退回。
    """
    def __init__(self, tp, threshold_ms=2000, poll_ms=35):
        self.tp = tp
        self.threshold_ms = threshold_ms
        self.poll_ms = poll_ms
        self._press_start = None
        self._last_poll = time.ticks_ms()

    def _read_xy(self):
        # 直接讀座標暫存（同 get_point() 使用的 register）
        # 若硬體/韌體不支援，則回傳 (0,0)
        try:
            b = self.tp._read_block(0x03, 4)  # [xh,xl,yh,yl]
            x = ((b[0] & 0x0F) << 8) | b[1]
            y = ((b[2] & 0x0F) << 8) | b[3]
            return x, y
        except Exception:
            return 0, 0

    def check(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_poll) < self.poll_ms:
            return
        self._last_poll = now

        x, y = self._read_xy()
        touching = (x != 0 or y != 0)

        if touching:
            if self._press_start is None:
                self._press_start = now
            elif time.ticks_diff(now, self._press_start) >= self.threshold_ms:
                raise AbortToMenu()
        else:
            self._press_start = None


def run_script(path):
    import gc, sys

    safe_clear()
    draw_center_lines(["RUN:", path], c_sel, y0=CY - 10)
    LCD.show()
    time.sleep_ms(150)

    # 先 GC，能回收多少算多少
    gc.collect()


    # --- 關鍵：避免腳本重新配置 115200 bytes FrameBuffer ---
    # 把 touch.LCD_1inch28 暫時改成回傳現成的 LCD（單例）
    _orig_lcd_ctor = touch.LCD_1inch28
    def _lcd_singleton(*a, **k):
        return LCD

    # 同理：避免腳本重複 new 觸控（可選，但通常也建議）
    _orig_tp_ctor = getattr(touch, "Touch_CST816T", None)

    # 你 menu 的 TouchAdapter 內已有 tp，可讓腳本拿同一顆（若你要）
    # 假設你在外面有全域 ta 或 menu.t.tp，這裡示範用 try 安全取用
    tp_singleton = None
    try:
        # 若你是 DialMenu(touch_adapter) 的結構，可把 tp 存成全域供這裡取
        # 例如在 main() 先 global TP_SINGLETON = ta.tp
        tp_singleton = TP_SINGLETON  # 如果你有做這個全域
    except Exception:
        tp_singleton = None

    # ---- 長按退回 Menu：在子程式執行期間監控 ----
    # 依賴 TP_SINGLETON（TouchAdapter 建立的 tp），若不存在則停用長按退回
    _guard = LongPressGuard(tp_singleton, threshold_ms=2000, poll_ms=35) if tp_singleton is not None else None

    def _tp_singleton(*a, **k):
        return tp_singleton if tp_singleton is not None else _orig_tp_ctor(*a, **k)

    try:
        touch.LCD_1inch28 = _lcd_singleton
        # ---- 子程式長按退回：hook time.sleep / time.sleep_ms / LCD.show ----
        _orig_sleep = getattr(time, "sleep", None)
        _orig_sleep_ms = getattr(time, "sleep_ms", None)
        _orig_show = getattr(LCD, "show", None)

        def _guard_check():
            if _guard is not None:
                _guard.check()

        def _sleep_hook(sec):
            # 將 sleep 切成小段，期間可偵測長按
            try:
                ms = int(sec * 1000)
            except Exception:
                ms = 0
            step = 30
            while ms > 0:
                _guard_check()
                if _orig_sleep_ms is not None:
                    _orig_sleep_ms(step if ms > step else ms)
                else:
                    if _orig_sleep is not None:
                        _orig_sleep((step if ms > step else ms) / 1000)
                ms -= step
            _guard_check()

        def _sleep_ms_hook(ms):
            try:
                ms = int(ms)
            except Exception:
                ms = 0
            step = 30
            while ms > 0:
                _guard_check()
                if _orig_sleep_ms is not None:
                    _orig_sleep_ms(step if ms > step else ms)
                else:
                    if _orig_sleep is not None:
                        _orig_sleep((step if ms > step else ms) / 1000)
                ms -= step
            _guard_check()

        def _show_hook(*a, **k):
            _guard_check()
            return _orig_show(*a, **k)

        if _orig_sleep is not None:
            time.sleep = _sleep_hook
        if _orig_sleep_ms is not None:
            time.sleep_ms = _sleep_ms_hook
        if _orig_show is not None:
            LCD.show = _show_hook
        if _orig_tp_ctor is not None and tp_singleton is not None:
            touch.Touch_CST816T = _tp_singleton

        # 用乾淨 namespace 執行，避免把 menu 的大量全域帶進去
        code = open(path, "r").read()
        g = {"__name__": "__main__", "__file__": path, "LCD": LCD, "touch": touch, "hw": hw}
        try:
            exec(code, g, g)
        except AbortToMenu:
            # 長按觸發：回到 Menu
            raise

        safe_clear()
        draw_center_lines(["DONE", path], c_sel, y0=CY - 10)
        LCD.show()
        time.sleep_ms(500)

    except AbortToMenu:
        safe_clear()
        draw_center_lines(["BACK", "to menu"], c_sel, y0=CY - 10)
        LCD.show()
        time.sleep_ms(350)

    except Exception as e:
        safe_clear()
        draw_center_lines(["ERROR", "see REPL"], c_err, y0=CY - 10)
        LCD.show()
        sys.print_exception(e)
        time.sleep_ms(900)

    finally:
        # 還原原本 constructor，避免影響 menu 後續行為
        # 還原 hook（子程式長按退回）
        try:
            if '_orig_sleep' in locals() and _orig_sleep is not None:
                time.sleep = _orig_sleep
            if '_orig_sleep_ms' in locals() and _orig_sleep_ms is not None:
                time.sleep_ms = _orig_sleep_ms
            if '_orig_show' in locals() and _orig_show is not None:
                LCD.show = _orig_show
        except Exception:
            pass

        touch.LCD_1inch28 = _orig_lcd_ctor
        if _orig_tp_ctor is not None:
            touch.Touch_CST816T = _orig_tp_ctor

        gc.collect()


# ------------------------------------------------------------
# 觸控 Adapter：依你的 Touch_CST816T 韌體行為設計
# - 觸控中斷來時：Touch.Flag=1 並更新 X_point/Y_point
# - 沒有「release」事件，所以用「最後事件時間 + 閒置超時」推定放開
# ------------------------------------------------------------
class TouchAdapter:
    def __init__(self):
        # 你的 touch.py Touch_CST816T 預設：i2c_sda=6,i2c_scl=7,int_pin=21,rst_pin=22
        self.tp = TP if TP is not None else touch.Touch_CST816T(mode=1)  # point mode (singleton preferred)
        try:
            self.tp.Mode = 1
            self.tp.Set_Mode(1)
        except Exception:
            pass

        # 供子程式長按退回使用（run_script 會讀這個）
        global TP_SINGLETON
        TP_SINGLETON = self.tp

        self.last_x = 0
        self.last_y = 0
        self.last_evt_ms = time.ticks_ms()
        self._pressed = False

        # release 推定閾值（毫秒）
        self.release_ms = 140

    def poll(self):
        """
        回傳：
          (pressed:bool, x:int, y:int, is_new:bool)
        is_new = True 代表這次有新觸控點（由中斷 Flag=1 觸發）
        """
        now = time.ticks_ms()

        is_new = False
        if getattr(self.tp, "Flag", 0) == 1:
            # 消耗一次事件
            self.tp.Flag = 0
            x = int(getattr(self.tp, "X_point", 0))
            y = int(getattr(self.tp, "Y_point", 0))
            # 你的韌體在無效時可能是 0；避免把 (0,0) 當有效點
            if x != 0 or y != 0:
                self.last_x, self.last_y = x, y
                self.last_evt_ms = now
                is_new = True

        # 用閒置時間推定 pressed/release
        if time.ticks_diff(now, self.last_evt_ms) <= self.release_ms:
            self._pressed = True
        else:
            self._pressed = False

        return (self._pressed, self.last_x, self.last_y, is_new)

# ------------------------------------------------------------
# 圓形表盤 Menu
# ------------------------------------------------------------
class DialMenu:
    def __init__(self, touch_adapter):
        self.t = touch_adapter
        self.items = list_py_files()
        self.n = len(self.items)
        self.idx = 0

        # 手勢狀態
        self.pressing = False
        self.down_x = 0
        self.down_y = 0
        self.down_ms = 0
        self.last_move_x = 0
        self.dragged = False

        # 顯示用：輕微旋轉感
        self.angle_offset = 0.0

        self.last_redraw = time.ticks_ms()

    def reload_items(self):
        self.items = list_py_files()
        self.n = len(self.items)
        self.idx = clamp(self.idx, 0, max(0, self.n - 1))

    def step_selection(self, delta):
        if self.n == 0:
            return
        self.idx = (self.idx + delta) % self.n

    def draw(self):
        safe_clear()

        # 外/內環
        draw_circle_outline(CX, CY, R_OUT, c_ring)
        draw_circle_outline(CX, CY, R_IN,  c_ring)

        if self.n == 0:
            draw_center_lines(["No .py files", "Put scripts in root"], c_dim)
            LCD.show()
            return

        # 顯示最多 8 個點位在環上
        show_k = min(8, self.n)
        half = show_k // 2

        base = -math.pi / 2  # 上方
        span = math.radians(240)
        step = span / max(1, show_k - 1)

        r_mid = (R_IN + R_OUT) // 2

        for i in range(show_k):
            j = (self.idx - half + i) % self.n
            a = base - span / 2 + i * step + self.angle_offset

            x = int(CX + r_mid * math.cos(a))
            y = int(CY + r_mid * math.sin(a))

            sel = (j == self.idx)
            col_dot = c_sel if sel else c_dim

            fill_circle(x, y, R_ICON if sel else (R_ICON - 4), col_dot)

            name = self.items[j][:-3]
            if len(name) > 8:
                name = name[:8] + "…"

            tx = x - (len(name) * 4)
            ty = y + (R_ICON + 2)
            LCD.text(name, tx, ty, c_txt if sel else c_dim)

        # 中央標題
        center = self.items[self.idx][:-3]
        if len(center) > 16:
            center = center[:16] + "…"
        draw_center_lines([center, "Tap: run", "Swipe: switch"], c_txt, y0=CY - 16)

        LCD.show()

    def handle_touch(self):
        pressed, x, y, is_new = self.t.poll()
        now = time.ticks_ms()

        # 沒有新事件就不處理移動（避免用舊座標亂判斷）
        if not is_new and pressed:
            return False

        if pressed and not self.pressing:
            # touch down（以第一個新點作為 down）
            self.pressing = True
            self.dragged = False
            self.down_x, self.down_y = x, y
            self.last_move_x = x
            self.down_ms = now
            self.angle_offset = 0.0
            return True

        if pressed and self.pressing and is_new:
            dx = x - self.down_x
            dy = y - self.down_y
            if dx * dx + dy * dy > 14 * 14:
                self.dragged = True

            ddx = x - self.last_move_x
            self.last_move_x = x

            # 視覺旋轉
            self.angle_offset += ddx * 0.002
            self.angle_offset = clamp(self.angle_offset, -0.6, 0.6)

            # 主要換項：水平拖曳超過門檻就切換一格
            if abs(dx) > 40:
                if dx > 0:
                    self.step_selection(-1)
                else:
                    self.step_selection(+1)
                # 重置基準避免連跳
                self.down_x = x
                self.angle_offset = 0.0

            return True

        if (not pressed) and self.pressing:
            # release（由閒置超時推定）
            self.pressing = False
            dt = time.ticks_diff(now, self.down_ms)
            self.angle_offset = 0.0

            # 若不是拖曳且按下時間短 => 點選
            if (not self.dragged) and dt < 380 and self.n > 0:
                run_script(self.items[self.idx])
                self.reload_items()
                return True

        return False

    def loop(self):
        self.draw()
        while True:
            changed = self.handle_touch()
            now = time.ticks_ms()

            # 互動就重畫；否則降頻
            if changed or time.ticks_diff(now, self.last_redraw) > 250:
                self.draw()
                self.last_redraw = now

            time.sleep_ms(12)
def main():
    global TP_SINGLETON
    ta = TouchAdapter()
    TP_SINGLETON = ta.tp  # 讓 run_script() 可以重用同一顆觸控
    menu = DialMenu(ta)
    menu.loop()


if __name__ == "__main__":
    main()
