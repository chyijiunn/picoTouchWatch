from hw import LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)        

LCD.pixel(120, 120, c)			#draw a pixel(x,y,c)
LCD.line(30,30,120,90,c)			#draw a line(xstart , ystart , xend , yend ,c)
LCD.fill_rect(170,100,20,20,c)	#draw a rectangle(xstart , ystart , xlength , ywidth,c)
LCD.fill_tri(40,160,150,170,140,140,c)#draw a triangle(3 pointsite ,c)

LCD.show()