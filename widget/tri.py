import touch
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)

color = LCD.color
LCD.set_bl_pwm(15535)
            
LCD.fill_tri(33,45,67,82,100,12,0x07E0)
LCD.show()
