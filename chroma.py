import os
import matplotlib.pyplot as plt
import skimage
from skimage import img_as_ubyte
from skimage import io
from skimage import filters


os.system('cls')
root = os.path.dirname(__file__)

def remove_green(img):

    norm_factor = 255

    """
    obtain the ratio of the green/red/blue
    channels based on the max-brightness of 
    the pixel
    """ 
    red_ratio = img[:, :, 0] / norm_factor
    green_ratio = img[:, :, 1] / norm_factor
    blue_ratio = img[:, :, 2] / norm_factor

    """
    darker pixels would be around 0.
    In order to ommit removing dark pixels we
    add .3 to make small negative numbers positive
    """
    
    red_vs_green = (red_ratio - green_ratio) + .3
    blue_vs_green = (blue_ratio - green_ratio) + .3

    """
    now pixels with a negative value would have a
    high probability to be background green
    pixels.
    """
    red_vs_green[red_vs_green < 0] = 0
    blue_vs_green[blue_vs_green < 0] = 0

    """
    combine the red_vs_green and blue_vs_green ratios
    to create an aplha mask
    """
    alpha = (red_vs_green + blue_vs_green) * 255
    alpha[alpha > 50] = 255

    img[:, :, 3] = alpha

    return img

def draw(bg, green):  
    fig, ax = plt.subplots(1, 2, sharex=True, sharey=True)
    fig.suptitle("close this window to continue")
    ax[1].imshow(green)
    ax[0].imshow(bg)
    plt.show()

def rotate(bg,green):
    r_list = [0,90,180,-90,-180]
    r = 1
    while(r not in r_list):
        r = int(input("enter the amount of rotation (0,90,180,-90,-180) ?...  "))
        if(r in r_list):
            green = skimage.transform.rotate(green, r, resize=True, mode='edge')
        else:
            print("\tinvalid value, try again")
    return green
    
def rescale(bg,green):
    h,w,_ = green.shape
    h1,w1,_ = bg.shape
    maxs = min(h1/h, w1/w) - 0.01
    s = 0.0
    maxs = round(maxs,2)
    while(s<0.1 or s>maxs):
        s = float(input("enter the amount of scaling (between 0.1 and " + str(maxs) + ") ?...  "))
        if(s>=0.1 and s<=maxs):
            green = skimage.transform.rescale(green, s, multichannel=True)
        else:
            print("\tinvalid value, try again")
    return green

def blur(bg,green):
    b = 'x'
    while(b!='y' and b!='Y' and b!='n' and b!='N'):
        b = input("do you want to blur the background (y/n) ?...  ")
        if(b=='y' or b=='Y'):
            bg = filters.gaussian(bg,sigma=5,multichannel=True)
        elif(b=='n' or b=='N'):
            break
        else:
            print("\tinvalid value, try again")
    return bg

def align(bg,green):
    h,w,_ = green.shape
    h1,w1,_ = bg.shape
    a = 0
    print("|1 2 3|")
    print("|4 5 6|")
    print("|7 8 9|")
    while(a<1 or a>9):
        a = int(input("enter the number corresponding to the required alignment...  "))
        if(a>=1 and a<=9):
            if(a==1): 
                coord=(0,0)
            elif(a==2): 
                coord=(0,int(w1/2-w/2))
            elif(a==3): 
                coord=(0,w1-w)
            elif(a==4): 
                coord=(int(h1/2-h/2),0)
            elif(a==5): 
                coord=(int(h1/2-h/2),int(w1/2-w/2))
            elif(a==6): 
                coord=(int(h1/2-h/2),w1-w)
            elif(a==7): 
                coord=(h1-h,0)
            elif(a==8): 
                coord=(h1-h,int(w1/2-w/2))
            elif(a==9): 
                coord=(h1-h,w1-w)
        else:
            print("\tinvalid value, try again")
    return coord

def blend(bg, green):
    
    draw(bg,green)

    green = remove_green(green)
    green = rotate(bg,green)
    green = rescale(bg,green)
    bg = blur(bg,green)
    coord = align(bg,green)

    green = img_as_ubyte(green)
    bg = img_as_ubyte(bg)
    (x_size, y_size, _) = green.shape

    (x_ini, y_ini) = coord
    x_end = x_ini + x_size
    y_end = y_ini + y_size

    bg_crop = bg[x_ini:x_end,y_ini:y_end,:]
    
    """
    only the part of "green" with alpha values higher than 10 are taken
    "bg" pixels are replaced with corresponding "green" pixels for this part
    """
    pixel_preserve = (green[:, :, -1] > 10)   

    bg_crop[pixel_preserve] = green[pixel_preserve]

    bg[x_ini:x_end, y_ini:y_end, :] = bg_crop

    return bg


print("*the program assumes that the pictures are in the correct folders*")

"""
"bg" is the background image and "green" is the image with the green background
"""

bg_path = input('enter name of background image...  ')
bg = skimage.io.imread(root + '/background/' + bg_path + '.jpg', pilmode="RGBA")

green_path = input('enter name of green screen image...  ')
green = skimage.io.imread(root + '/with green screen/' + green_path + '.jpg', pilmode="RGBA")

img = blend(bg,green)

plt.imshow(img)
plt.show()

x = 'x'
while(x!='s' and x!='S'):
    x = input("enter 's' to save the image, 't' to try again, 'e' to exit...  ")
    print()
    if(x=='t' or x=='T'):
        bg = skimage.io.imread(root+'/background/' + bg_path, pilmode="RGBA")
        green = skimage.io.imread(root+'/with green screen/' + green_path, pilmode="RGBA")
        img = blend(bg,green)
        plt.imshow(img)
        plt.show()
    elif(x=='s' or x=='S'):
        break
    elif(x=='e' or x=='E'):
        exit()
    else:
        print("\tinvalid value, try again")

save_path = input('enter name you want to save the image with...  ')
plt.axis("off")
plt.imshow(img)
plt.savefig(root + '/exports/' + save_path +'.png',bbox_inches='tight',pad_inches=0,dpi=300)
