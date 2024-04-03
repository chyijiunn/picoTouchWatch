'''
修改自 imgtobitmap.py
於終端機輸入 python3 18_imgtobitmapSavePy.py media/filename.bmp 8
注意檔案大小建議 120*120 -> 8 bit , 180*180 -> 7bit 
執行結束儲存成 bmp.py
'''
from PIL import Image
import argparse

def main():

    parser = argparse.ArgumentParser(
        prog='imgtobitmap',
        description='Convert image file to python module for use with bitmap method.')
    parser.add_argument(
        'image_file',
        help='Name of file containing image to convert')
    parser.add_argument(
        'bits_per_pixel',
        type=int,
        choices=range(1, 9),
        default=1,
        metavar='bits_per_pixel',
        help='The number of bits to use per pixel (1..8)')

    args = parser.parse_args()

    bits = args.bits_per_pixel
    img = Image.open(args.image_file)
    img = img.convert("P", palette=Image.ADAPTIVE, colors=2**bits)
    palette = img.getpalette()  # Make copy of palette colors

    # For all the colors in the palette
    colors = []
    for color in range(1 << bits):

        # get rgb values and convert to 565
        color565 = (
            ((palette[color*3] & 0xF8) << 8)
            | ((palette[color*3+1] & 0xFC) << 3)
            | ((palette[color*3+2] & 0xF8) >> 3))

        # swap bytes in 565
        color = ((color565 & 0xff) << 8) + ((color565 & 0xff00) >> 8)

        # append byte swapped 565 color to colors
        colors.append(f'{color:04x}')

    image_bitstring = ''
    max_colors = 1 << bits

    # Run through the image and create a string with the ascii binary
    # representation of the color of each pixel.
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            color = pixel
            bstring = ''
            for bit in range(bits, 0, -1):
                bstring += '1' if (color & (1 << bit-1)) else '0'
            image_bitstring += bstring

    bitmap_bits = len(image_bitstring)

    # Create python source with image parameters
    
    data = open('bmp.py','w')
    data.write(f'HEIGHT = {img.height}'+'\n')
    data.write(f'WIDTH = {img.width}'+'\n')
    data.write(f'COLORS = {max_colors}'+'\n')
    data.write(f'BITS = {bitmap_bits}'+'\n')
    data.write(f'BPP = {bits}'+'\n')
    data.write('PALETTE = [')

    for color, rgb in enumerate(colors):
        if color:
            data.write(',')
        data.write(str(f'0x{rgb}'))
    data.write("]"+'\n')

    # Run though image bit string 8 bits at a time
    # and create python array source for memoryview

    data.write("_bitmap =\\"+'\n')
    data.write("b'")

    for i in range(0, bitmap_bits, 8):

        if i and i % (16*8) == 0:
            data.write("'\\\nb'")

        value = image_bitstring[i:i+8]
        color = int(value, 2)
        data.write(str(f'\\x{color:02x}'))

    data.write("'\nBITMAP = memoryview(_bitmap)")
    data.close()
main()
