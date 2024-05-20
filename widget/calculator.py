import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
color = LCD.color
LCD.set_bl_pwm(15535)
BG = color(0,0,0)
c1 = color(120,120,120)
c2 = color(255,255,255)
LCD.fill(BG)
LCD.show()

expression = ""#顯示空字串

def draw_button(x, y, w, h, label):
    LCD.fill_rect(x, y, w, h, c1)
    LCD.text(label, x + w//4, y + h//4,c2)
    
def draw_buttons():
    buttons = [
        ('7', 60, 90), ('8', 90, 90), ('9', 120, 90), ('/', 150, 90),
        ('4', 60, 120), ('5', 90, 120), ('6', 120, 120), ('x', 150, 120),
        ('1', 60, 150), ('2', 90, 150), ('3', 120, 150), ('-', 150, 150),
        ('0', 60, 180), ('C', 90, 180), ('=', 120, 180), ('+', 150, 180),
        ]
    for label, x, y in buttons:
        draw_button(x, y, 25, 25, label)

def update_display(expression):
    LCD.fill_rect(0, 0, 240, 90, BG)
    shift = int(16*len(list(expression)))
    LCD.write_text(expression, 200-shift, 60,2 , c2)
    LCD.show()

draw_buttons()
update_display(expression)
LCD.show()

Touch.Flgh = 0
Touch.Flag = 0
while True:
    if Touch.Flag == 1:
        x , y = Touch.X_point , Touch.Y_point
        
        if y > 90:  # 判斷是否於按鈕區
            col = (x-60) // 30
            row = (y - 90) // 30
            index = row * 4 + col
            buttons = '789/456*123-0C=+'
            if index < len(buttons):
                char = buttons[index]
                if char == 'C':
                    expression = ""
                elif char == '=':
                    try:
                        expression = str(eval(expression))
                    except:
                        expression = "Error"
                else:
                    expression += char
                update_display(expression)
            
        time.sleep(0.2)
        Touch.Flag = 0