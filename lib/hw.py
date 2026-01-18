import touch

LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

IMU = touch.QMI8658()

TP = touch.Touch_CST816T(mode=1,i2c_num=1,i2c_sda=touch.I2C_SDA,i2c_scl=touch.I2C_SDL,int_pin=touch.I2C_INT,rst_pin=touch.I2C_RST)
TP.Mode = 1
TP.Set_Mode(1)
