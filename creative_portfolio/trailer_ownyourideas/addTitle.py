#!/usr/local/bin/python3
import sys
import json
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps
import shutil
import zipfile



if len(sys.argv) < 2:
    cmd = "{0} <title input>"
    print(cmd.format(sys.argv[0]))
    print("Where:")
    legend = "".join([
        "\t<title input>: title, audiences, topics description file ",
        "in JSON format",
    ])
    print(legend)
    sys.exit()

title = json.load(open(sys.argv[1], "r"))
#print(title)



DEBUG = True
#TITLE_FONT = ImageFont.truetype("Segoe Print", 72)
TITLE_FONT    = ImageFont.truetype("c:\\Windows\\Fonts\\segoepr.ttf", 72)
AUDIENCE_FONT = ImageFont.truetype("c:\\Windows\\Fonts\\times.ttf", 48) # 36
START_FRAME   = 98
END_FRAME     = START_FRAME + 100



def setTransparent(img):
    (width, height) = img.size
    #img = img.convert("RGBA")
    for y in range(0, height):
        for x in range(0, width):
            rgb = img.getpixel((x, y))
            if (rgb[0] == 255) and (rgb[1] == 255) and (rgb[2] == 255):
                rgb = (rgb[0], rgb[1], rgb[2], 0)
                img.putpixel((x, y), rgb)
    return img

def drawTitleVerticalClipRegion(img):
    for y in range(0, 534):
        #for x in range(1634, 1920):
        for x in range(1770, 1920):
            rgb = img.getpixel((x, y))
            rgb = (rgb[0], rgb[1], rgb[2], 255)
            img.putpixel((x, y), rgb)
    return img

def imgWidth(img):
    (width, height) = img.size
    for x in reversed(range(0, width)):
        found = False
        for y in range(0, height):
            rgb = img.getpixel((x, y))
            if not((rgb[0] == 255) and (rgb[1] == 255) and (rgb[2] == 255)):
                found = True
                break
        if found:
            return x + 1
    return -1

def drawText(txt):
    img = Image.new('RGBA', (1080, 122), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), txt, fill=(63, 72, 204, 255), font=TITLE_FONT)
    #img = ImageOps.fit(img, (1000, 122), Image.ANTIALIAS)
    width = imgWidth(img)
    if width > 0:
        img = Image.new('RGBA', (width, 122), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), txt, fill=(63, 72, 204, 255), font=TITLE_FONT)
    return img

def drawAudience(audiences, topics):
    START_LINE = 600
    txtColour = (0, 0, 0, 255)
    img = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    # audiences
    draw.text((100, START_LINE), "Audiences:", fill=txtColour, font=AUDIENCE_FONT)
    line = START_LINE
    for audience in audiences:
        line += (52 + 8)
        draw.text((100 + 60, line), audience, fill=txtColour, font=AUDIENCE_FONT)
    # topics
    draw.text((1300, START_LINE), "Topics:", fill=txtColour, font=AUDIENCE_FONT)
    line = START_LINE
    for topic in topics:
        line += (52 + 8)
        draw.text((1300 + 60, line), topic, fill=txtColour, font=AUDIENCE_FONT)
        #draw.text((1202 + 60, line), topic, fill=txtColour, font=AUDIENCE_FONT)
    return img

def createAudienceLayer():
    try:
        shutil.rmtree("./ownyourideas")
    except:
        pass
    with zipfile.ZipFile("./ownyourideas.tpl", 'r') as zip_ref:
        zip_ref.extractall("./ownyourideas")
    img = drawAudience(title["audiences"], title["topics"])
    # Do fade
    alpha = 1.0
    opImg = Image.new('RGBA', img.size, (255, 255, 255, 255))
    stillImg = None
    for idx in range(START_FRAME, END_FRAME):
        print("Create frame: " + str(idx))
        fileName = "013.{:03d}".format(idx) + ".png"
        fileName = "./ownyourideas/data/" + fileName
        if DEBUG:
            alpha -= 0.3
        else:
            alpha -= 0.025
        if alpha < 0:
            alpha = 0.0
        else:
            frameImg = Image.blend(img, opImg, alpha)
            frameImg = setTransparent(frameImg)
            frameImg = drawTitleVerticalClipRegion(frameImg)
            stillImg = frameImg
        stillImg.save(fileName)



lineCount = len(title['title'])
LINE_BREAK = "\n"
if lineCount == 1:
    # create Title Layer Frame
    titleImg = drawText(title['title'][0])
    (titleW, titleH) = titleImg.size
    if titleW > 874:
        print("Title width size must be limitted to 874 pixels.")
        sys.exit()

    createAudienceLayer()

    # main.xml: create layer 12
    mainTplFile = open("./ownyourideas.xml")
    bufStr = mainTplFile.read()
    bufStr += LINE_BREAK + '    '
    bufStr += '<layer id="12" visibility="1" name="Title" type="1">'
    titleDiff = 874 - titleW
    # For width = 874    : x = -57
    # For width = 874 - 2: x = -57 + 1
    # 2 = titleDiff ->     x = -57 + titleDiff / 2
    topLeftX = -57 + int(titleDiff / 2)
    for idx in reversed(range(START_FRAME, END_FRAME)):
        fileName = "012.{:03d}".format(idx) + ".png"
        fileName = "./ownyourideas/data/" + fileName
        titleImg.save(fileName)
        bufStr += LINE_BREAK + '      '
        bufStr += '<image topLeftY="-295" frame="{:d}" topLeftX="{:d}" src="012.{:03d}.png"/>'.format(idx, topLeftX, idx)
    bufStr += LINE_BREAK + '      '
    bufStr += '<image topLeftY="0" frame="1" topLeftX="0" src="012.001.png"/>'
    bufStr += LINE_BREAK + '    '
    bufStr += '</layer>'

    # main.xml: create layer 13
    bufStr += LINE_BREAK + '    '
    bufStr += '<layer id="13" visibility="1" name="Audiences" type="1">'
    for idx in reversed(range(START_FRAME, END_FRAME)):
        bufStr += LINE_BREAK + '      '
        bufStr += '<image frame="{:d}" topLeftX="-960" topLeftY="-540" src="013.{:03d}.png"/>'.format(idx, idx)
    bufStr += LINE_BREAK + '      '
    bufStr += '<image frame="1" topLeftX="0" topLeftY="0" src="013.001.png"/>'
    bufStr += LINE_BREAK + '    '
    bufStr += '</layer>'
    bufStr += LINE_BREAK + '  '
    bufStr += '</object>'
    bufStr += LINE_BREAK
    bufStr += '</document>'
    mainXml = open("./ownyourideas/main.xml", "w")
    mainXml.write(bufStr)
    mainXml.close()

    # zip it into a Pencil2D file
    shutil.make_archive("./release", "zip", "./ownyourideas")
    shutil.move("./release.zip", "./release.pclx")
elif lineCount == 2:
    pass