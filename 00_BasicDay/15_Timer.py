from machine import Timer
tim1 = Timer(-1)
tim2 = Timer(-1)
tim1.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:print('ok_1'))
tim2.init(period=2000, mode=Timer.PERIODIC, callback=lambda t:print('ok_2'))