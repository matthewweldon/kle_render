from PIL import Image, ImageMath, ImageColor, ImageDraw, ImageFont

# Key and deserialise() modified from https://github.com/jackhumbert/kle-image-creator
class Key(object):

    base_img = Image.open(r'SA_base.jpg').convert('RGBA') # SA photo by Madhias (Deskthority), GMK from official renders
    u = base_img.width
    font_path = r'NotoRounded.otf'

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.x2 =0.0
        self.y2 = 0.0
        self.width = 1.0
        self.height = 1.0
        self.width2 = 1.0
        self.height2 = 1.0
        self.color = '#EEE2D0'
        self.font_color = '#000000'
        self.labels =[]
        self.align = 4
        self.font_size = 8.0
        self.font_size2 = 8.0
        self.rotation_angle = 0.0
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.profile = ''
        self.nub = False
        self.ghost = False
        self.stepped = False
        self.decal = False

    def location(self): # get pixel location of key as (left, upper, right, lower)
        u = self.u
        return (int(self.x*u), int(self.y*u), int(self.x*u + self.width*u), int(self.y*u + self.height*u))

    def tint_key(self, key_img): #a image of the key, and a hex color code string
        color = ImageColor.getrgb(self.color)
        r, g, b, a = key_img.split()
        r = ImageMath.eval('a - 0xE0 + c', a=r, c=color[0]).convert('L') #base image is a desaturated WFK key, and desaturated WFK is e0e0e0
        g = ImageMath.eval('a - 0xE0 + c', a=g, c=color[1]).convert('L')
        b = ImageMath.eval('a - 0xE0 + c', a=b, c=color[2]).convert('L')
        return Image.merge('RGBA', (r, g, b, a))

    def stretch_key(self): # width and height of key in units
        base_img = self.base_img
        u = self.u
        if self.width == 1.0 and self.height == 1.0:
            return base_img
        else:
            width, height = int(self.width*u), int(self.height*u) # Width & Height of image representing key
            key_img = Image.new('RGBA', (width, height))
            key_img.paste(base_img, (0, 0, u, u))
            if width != u:
                center_part = base_img.crop((int(u/2), 0, int(u/2) + 1, u)) # horizontal middle strip of image
                right_part = base_img.crop((int(u/2) + 1, 0, u, u))
                for i in range(width - u + 1):
                    key_img.paste(center_part, (int(u/2) + i, 0, int(u/2) + i + 1, u))
                key_img.paste(right_part, (width - right_part.width, 0, width, u))
            if height != u:
                middle_part = key_img.crop((0, int(u/2), width, int(u/2) + 1)) # vertical middle strip of image
                bottom_part = key_img.crop((0, int(u/2) + 1, width, u))
                key_img.paste(bottom_part, (0, height - bottom_part.height, width, height))
                for i in range(height - u + 1):
                    key_img.paste(middle_part, (0, int(u/2) + i, key_img.width, int(u/2) + i + 1))
            return key_img

    def decal_key(self):
        key_img = Image.new('RGBA', (int(self.width*self.u), int(self.height*self.u)))
        return key_img

    def text_key(self, key_img): # convert for use with list of labels
        scale_factor = 7
        min_size = 24
        line_spacing = 20
        offset = 20 # pixels to shift text upwards to center it in keycap top
        labels = [text.upper() for text in self.labels] # only uppercase text on SA

        gotham = ImageFont.truetype(self.font_path, int(self.font_size*scale_factor)+min_size)
        draw = ImageDraw.Draw(key_img)
        w = max([gotham.getsize(text)[0] for text in labels]) # max of widths
        h = sum([gotham.getsize(text)[1] for text in labels]) # sum of heights
        h += line_spacing*(len([text for text in labels if len(text) > 0])-1)
        c = ImageColor.getrgb(self.font_color)
        c = tuple(band + 0x26 for band in c) # Simulates reflectivity
        draw.multiline_text((int((key_img.width-w)/2), int((key_img.height-h)/2 - offset)), '\n'.join(labels), font=gotham, fill=c, spacing=line_spacing, align='center')
        return key_img 

    def render(self):
        if self.decal:
            key_img = self.decal_key()
        else:
            key_img = self.stretch_key()
            key_img = self.tint_key(key_img)
        key_img = self.text_key(key_img)
        return key_img
