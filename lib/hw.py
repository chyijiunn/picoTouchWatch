# hw.py
import touch
# ===== LCD =====
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
# ===== IMU =====
IMU = touch.QMI8658()
# ===== Touch Panel =====
TP = touch.Touch_CST816T(mode=1, LCD=LCD)
TP.Mode = 1
TP.Set_Mode(1)
