from PIL import Image
import cv2
import os

def tojpg(path):
    list = os.listdir(path)
    for i in range(0,len(list)):
        Uri = os.path.join(path,list[i])
        if os.path.isfile(Uri):
            f, e = os.path.splitext(Uri)
            outfile = f + '.jpg'
            if f != outfile and e =='png':
                try:
                    print(f)
                    print(outfile)
                    im = Image.open(Uri)
                    im.save(outfile)
                except IOError:
                    print("出现错误了")
if __name__ == '__main__':
    tojpg("./其它/vx_images/")