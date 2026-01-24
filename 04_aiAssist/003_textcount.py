from hw import LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
c1 = LCD.color(255,0,0)

size = 3
alphabet = 'HwWh'
lenth_alphabet = len(alphabet)

print(lenth_alphabet)

LCD.fill_rect(40,40,8*size*lenth_alphabet,size*8,c1)
LCD.write_text(alphabet,40,40,size,c)

LCD.show()
