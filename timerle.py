import gizeh
import numpy
from scipy import misc
#import Image
import socket
import time

GAMMA = 1.0
UDP_PORT = 1337

def alpha_to_color(image, color=(0, 0, 0)):
    """Set all fully transparent pixels of an RGBA image to the specified color.
    This is a very simple solution that might leave over some ugly edges, due
    to semi-transparent areas. You should use alpha_composite_with color instead.

    Source: http://stackoverflow.com/a/9166671/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """ 
    x = numpy.array(image)
    r, g, b, a = numpy.rollaxis(x, axis=-1)
    r[a == 0] = color[0]
    g[a == 0] = color[1]
    b[a == 0] = color[2] 
    x = numpy.dstack([r, g, b, a])
    return x
    #return Image.fromarray(x, 'RGBA')


def send_array(data, hostname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (hostname, UDP_PORT))

def prepare_message(data, unpack=False, gamma=GAMMA):
    """Prepares the pixel data for transmission over UDP
    """
    # 4 bytes for future use as a crc32 checksum in network byte order.
    checksum = bytearray([0,0,0,0])
    data_as_bytes = bytearray()
    if unpack:
        for r, g, b, a in data:
            r = int(((r/255.0) ** gamma) * 255 * BRIGHTNESS)
            g = int(((g/255.0) ** gamma) * 255 * BRIGHTNESS)
            b = int(((b/255.0) ** gamma) * 255 * BRIGHTNESS)
            data_as_bytes += bytearray([r,g,b])
    else:
        data_as_bytes = bytearray(data)
        
    while len(data_as_bytes) < 1920:
        data_as_bytes += bytearray([0,0,0])
    
    message = data_as_bytes + checksum
    return message


def draw_seconds(seconds):
    center = numpy.array([40/2, 16/2])

    surface = gizeh.Surface(width=40, height=16, bg_color=(0,0,0)) # in pixels

    image = alpha_to_color(misc.imread('alpaka.png'))
    alpaka = gizeh.ImagePattern(image, pixel_zero=center)

    r = gizeh.rectangle(lx=40, ly=16, xy=(24,8), fill=alpaka)
    r.draw(surface)

    text = gizeh.text("{:02d}".format(seconds), fontfamily="DIN Condensed",  fontsize=20,
                      fill=(0.99, 0.82, 0.25), xy=(32, 8), angle=0)# Pi/12)
    text.draw(surface)

    #surface.write_to_png("circle.png")
    out = surface.get_npimage()
    fb = out.tobytes()

    prepped = prepare_message(fb, unpack=False)
    send_array(prepped, '100.100.218.106')


def main():
    s = 40
    while(s > 0):
        print(s, ' ', )
        time.sleep(0.5)
        draw_seconds(s)
        time.sleep(0.5)
        draw_seconds(s)
        s -= 1
    print("---")
    while True:
        draw_seconds(s)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
