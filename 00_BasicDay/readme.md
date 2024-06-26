# 利用 RP2040 下個錶面功夫
1. 引入寫好的範例
	1. 畫一個長方形，包含座標資料、顏色
	2. 上寫一小段文字，包含座標、顏色![01](pics/01.jpg)
2. 讀取系統時間
	1. 設定亮度
	2. 利用LCD.text(需要為字串,x,y,顏色)
			- 字串= str()
			- 年,月,日,時,分,秒,星期,一年的第幾天,夏令時間![02](pics/02.jpg)
1. list下標使用，讀取 時、分、秒，分別為 [3] ~ [5]![03](pics/03.jpg)
2. 重複刷新螢幕時間，遇到問題：
	1. 停頓該多久
	2. 更新問題![04](pics/04.GIF)
3. 利用局部更新，替換掉前一秒，改用全部刷新又如何？![05](pics/05.GIF)
4. 做一個水鐘，每過一秒水位會上升一點
![06](pics/06.png)
	- 因為螢幕大小為240x240，若60秒跑完240個畫素，則每一秒上升 4 個畫素
	- 上升水位到 60秒時得全滿還是排空？
			- 實際上沒有 60 秒，即 59 秒後就必須歸零。
				- 如何更新？
					- 螢幕的刷新需要搭配底部顏色跟著上升
			
	- 圖層概念
		- 要在最上面的，程式碼後面再執行
		- 當圖層較多，局部更新也得變多層
			- 乾脆螢幕全部刷新![06](pics/06.GIF)
1. 把分也加入，停頓的時間設定多少比較省資源呢？![07](pics/07.GIF)
2. 為了指針表面，引入三角函數，需餵弧度、而非角度!
3. 考量秒針長度、設定 LCD.line(x,y起始點,x,y結束點,顏色)![08](pics/08.png)![09](pics/09.GIF)
4. 加入分針設計，比較一下是否有重複程式碼可以函示表示(tic , spinLen ,color ) = (time[] , 指針長度 ,顏色)![10](pics/10.GIF)
5. 時針設計加入，時針刻度每小時走30˚、每分鐘走 0.5˚
6. 秒針設計可以是
	1. 傳統秒針 def spin
	2. 同心圓秒針 def centerCircle
	3. 紅點設計繞行秒針 def runDotRing![12](pics/12.GIF)
7. 換顏色，學習[配色](https://coolors.co/generate)
	1. RGB888 --> RGB565[顏色轉換](https://blog.csdn.net/ctthuangcheng/article/details/8551559)
	2. << , >> [位數轉換](https://blog.csdn.net/weixin_37598106/article/details/116700903)
	3. 位移 .scroll(x,y)，以整個畫面為單位，每次位移 x , y 分別為多少![13](pics/13.GIF)
8. 引入 random 來決定顏色，random.randint(0,256) 從0~255選一個顏色![14](pics/14.GIF)
9. Timer 使用
10. 60秒才換一次顏色![16](pics/16.GIF)
11. 三軸讀取![17](pics/17.jpg)
12. 動了就爆炸 ![18](pics/18.GIF)
13. 利用六軸來節省電力 def powerSaver：
	- 如果沒有動，螢幕逐漸變暗
	- 不然就發亮 ![20](pics/20.GIF)
14. 檔案寫入
15. 省多少電？把時間、電壓寫入檔案![](pics/bat.png)
16. 下回合完成手錶錶殼 ![](pics/next.GIF)