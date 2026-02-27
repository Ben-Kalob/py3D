import qmath

from PIL import ImageTk, Image

from SysNav import get_real_path

def load_image(img_path : str,scale : float = 1) -> ImageTk.PhotoImage :
    np : str = get_real_path(img_path)
    img = Image.open(np)
    if scale >= 0.01 :
        scale = qmath.clampf(scale,0.1,5)
        img = img.resize(size = (int(img.width*scale),int(img.height*scale)),resample=0)
    return ImageTk.PhotoImage(image=img)
