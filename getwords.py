#!/usr/bin/python

############fbb nyu 2013
##created by federica bianco 
##strips the titles from the past 7 days of arxiv.org posts and creates a word cloud 
###
##uses BeautifulSoup to parse the arxiv url
###
##uses simple regex methods to estimate word frequency and a list is provided to remove common words
##more complicated algorythms tend to eliminate words that are common but significant 
##i think this is because we use titles, not real text with proper syntax
##for example sklearn CountVectorizer()
##
##the word cloud machinary that actually does the drawing is heavily stripped from 
##Andreas Mueller word cloud avaialble on github here https://github.com/amueller/word_cloud
##with modifications so that neither Cython nor scipy are needed
##
##this version also copies the image to a location in my path so that it is displayed on my website


import os,sys,re
import random
import datetime
import urllib2
from string import Template,punctuation
import numpy as np

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


from query_integral_image import query_integral_image
from BeautifulSoup import BeautifulSoup as bs


FONT_PATH = "./DroidSansMono.ttf"
MINCOUNTS=5
commonastrowords=['non','low','possible','probing','positive','negative','new','high','find','found','demonstrate','me','I','proof','prove','the','a','in','with','that','this','those','them','for', 'from','?','and','lat','long',':','.','of', 'used','using','use', 'lac']


class wordcloud:

    """Build word cloud using word counts, store in image.
    modified from Andreas Mueller word cloud avaialble on github here https://github.com/amueller/word_cloud
    Notes
    -----
    Larger Images with make the code significantly slower.
    If you need a large image, you can try running the algorithm at a lower
    resolution and then drawing the result at the desired resolution.

    In the current form it actually just uses the rank of the counts,
    i.e. the relative differences don't matter.
    Play with setting the font_size in the main loop vor differnt styles.

    Colors are used completely at random. Currently the colors are sampled
    from HSV space with a fixed S and V.
    Adjusting the percentages at the very end gives differnt color ranges.
    Obviously you can also set all at random - haven't tried that.

    """

    def __init__(self,words, counts, fname, font_path,width=400, height=200,margin=5):
        self.counts = counts
        self.words = words
        self.fname=fname
        self.width=width
        self.height=height
        self.font_path=font_path
        self.margin=margin

        check=self.checkit()
        if check == -1:
            return check
        
        self.draw().save(fname)


    def checkit(self):
        if len(self.counts) <= 0:
            print("We need at least 1 word to plot a word cloud, got %d."
                  % len(counts))
            return -1
        
        ####prepping:
        # normalize counts
        self.counts /= float(self.counts.max())
        # sort words by counts and cut to first 200
        inds = np.argsort(self.counts)[::-1]
        self.counts = self.counts[inds][:200]
        self.words = self.words[inds][:200]

    def draw(self):
        #### create image
        bwimg = Image.new("L", (self.width, self.height))
        draw = ImageDraw.Draw(bwimg)
        integral = np.zeros((self.height, self.width), dtype=np.uint32)
        img_array = np.asarray(bwimg)
        font_sizes, positions, orientations = [], [], []
        font_size = 1000
        
        # start drawing grey image
        for word, count in zip(self.words, self.counts):
            # alternative way to set the font size
            while True:
            # try to find a position
                font = ImageFont.truetype(self.font_path, font_size)
            # transpose font optionally
                orientation = random.choice([None, Image.ROTATE_90])
                transposed_font = ImageFont.TransposedFont(font,
                                                           orientation=orientation)
                draw.setfont(transposed_font)
            # get size of resulting text
                box_size = draw.textsize(word)
            # find possible places using integral image:
                result = query_integral_image(integral, box_size[1] + self.margin,
                                              box_size[0] + self.margin)
                if result is not None or font_size == 0:
                    break
            # if we didn't find a place, make font smaller
                font_size -= 1
            if font_size == 0:
            # we were unable to draw any more
                break

            x, y = np.array(result) + self.margin // 2
            # actually draw the text
            draw.text((y, x), word, fill="white")
            positions.append((x, y))
            orientations.append(orientation)
            font_sizes.append(font_size)
        # recompute integral image
            img_array = np.asarray(bwimg)
            # recompute bottom right
            # the order of the cumsum's is important for speed ?!
            partial_integral = np.cumsum(np.cumsum(img_array[x:, y:], axis=1),
                                         axis=0)
            # paste recomputed part into old image
        # if x or y is zero it is a bit annoying
            if x > 0:
                if y > 0:
                    partial_integral += (integral[x - 1, y:]
                                         - integral[x - 1, y - 1])
                else:
                    partial_integral += integral[x - 1, y:]
            if y > 0:
                partial_integral += integral[x:, y - 1][:, np.newaxis]

            integral[x:, y:] = partial_integral

    # redraw in color
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)
        everything = zip(self.words, font_sizes, positions, orientations)
        for word, font_size, position, orientation in everything:
            font = ImageFont.truetype(self.font_path, font_size)
            transposed_font = ImageFont.TransposedFont(font,
                                                       orientation=orientation)
            draw.setfont(transposed_font)
            draw.text((position[1], position[0]), word,
                      fill="hsl(%d" % random.randint(0, 255) + ", 80%, 50%)")

        #img.show()
        return img

    
def mycounter(s):
    mydic = {}
    for w in set(s.split()):
        print w,len(re.findall(w, s))
        if len(w)<3:
            continue
        try:
            mydic[w] = len(re.findall(w,s))
        except:
            pass
    return mydic

if __name__ == "__main__":

    url="http://arxiv.org/list/astro-ph/recent"
    response=urllib2.urlopen(url)
    html = response.read()
    soup = bs(html)
    m= re.search(r'total of (...)', soup.getText())
    totentries=int(m.group(1))
    url="http://arxiv.org/list/astro-ph/pastweek?show=%d"%totentries
    response=urllib2.urlopen(url)
    html = response.read()
    soup = bs(html)
    all = soup.findAll(attrs={'class':re.compile("list-title")})
    alltitles=[]

    for i in all:
        alltitles.append(i.text.replace("Title:","").strip())
    mywords= ' '.join(alltitles)

    exclude = set(punctuation)
    for w in exclude:
        mywords=mywords.replace(w,' ')
    for w in commonastrowords:
        mywords=mywords.lower().replace("-"," ").replace(" "+w+" "," ")
    mycounts=mycounter(mywords)
    
    words=[]
    counts=[]
    for k in mycounts.iterkeys():
        words.append(k)
        counts.append(mycounts[k])
    words=np.array(words)
    counts=np.array(counts)

    words = words[counts > MINCOUNTS]
    counts = counts[counts > MINCOUNTS]
    
    output_filename = "%s/cloud.png"%datetime.date.today()
    print output_filename
    os.system("mkdir %s"%datetime.date.today())
    cloud = wordcloud(words, counts, output_filename,font_path=FONT_PATH)
    os.system("cp %s ../videos/thisweekarxiv.png "%output_filename)
    os.system("chmod 644  ../videos/thisweekarxiv.png ")
    
