from hw import LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
c1 = LCD.color(255,0,0)

LCD.fill_rect(40,40,8,8,c1)
LCD.write_text('H',40,40,1,c)

LCD.fill_rect(40,60,16,16,c1)
LCD.write_text('H',40,60,2,c)

LCD.fill_rect(40,80,24,24,c1)
LCD.write_text('H',40,80,3,c)

LCD.fill_rect(40,120,32,32,c1)
LCD.write_text('W',40,120,4,c)

LCD.fill_rect(40,160,40,40,c1)
LCD.write_text('Hh',40,160,5,c)
LCD.show()
