# Pulls memes from Reddit
# TODO: Should it come from a different database? A variety? Not all DBs have authors
# If no author, could get actual DB

# TODO: refactor

import requests
import random
import pygame
import io
import time
from urllib.request import urlopen


import constants

memeHistory = []
memeCaptionHistory = []
memeAuthorHistory = []
activeMemeNum = -1
# references a meme count that is reset once it hits 20
# When reset, a new json file is produced
# So, each call (in sets of 20) won't need to make a get request, only parse the json file
i = -1


# The following piece of code was taken off of the web
# Think of it as a module
# http://www.pygame.org/pcr/transform_scale/
def aspect_scale(image, bx, by):
    ix, iy = image.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    return pygame.transform.scale(image, (int(sx), int(sy)))


def generateJSON():
    global json_object, activeMemeNum, i
    if activeMemeNum == len(memeHistory)-1:
        i += 1
        # Checks to see the amount of memes generated with the current json, if over 20, generates new json
        if not(0 < i < 21):
            # Checks if program needs to render a new meme
            # pulls JSON data from r/dankmemes (top posts from the day)
            if (random.randint(0, 2)) == 1:
                r = requests.get('https://www.reddit.com/r/dankmemes.json?raw json=1&sort=top&t=day', headers={'User-agent': 'your bot 0.1'})
            else:
                r = requests.get('https://www.reddit.com/r/memes.json?raw json=1&sort=top&t=day', headers={'User-agent': 'your bot 0.1'})
            json_object = r.json()
            if not activeMemeNum == -1:
                i == 1
    upperRange = len(json_object["data"]["children"])-1
    # defines upper range so code doesn't pull a post that doesn't exist
    # finds the post number
    memeNumber = random.randint(1, upperRange)
    # if new json is created, returns it
    # If there is no new json, it will return global json
    return json_object, memeNumber


def createNewMeme():
    global memeNumber, json_object, activeMemeNum
    json, memeNumber = generateJSON()
    for title in memeCaptionHistory:
        if title == json["data"]["children"][memeNumber]["data"]["title"]:
            json, memeNumber = generateJSON()
    activeMemeNum += 1
    # collects URL of desired meme
    memeURL = json["data"]["children"][memeNumber]["data"]["url"]
    title = json["data"]["children"][memeNumber]["data"]["title"]
    author = json["data"]["children"][memeNumber]["data"]["author"]
    memeHistory.append(memeURL)
    memeCaptionHistory.append(title)
    # Grabs the author
    memeAuthorHistory.append(author)
    # Displays caption
    displayText(title, constants.titleFontSize, 50, "title")
    # Displays author
    displayText("By " + author, int(constants.titleFontSize / 1.5), 85, "author")
    # Updates activeMemeNumber
    displayNum(20)
    initMeme(memeURL)
    pygame.display.flip()


def initMeme(memeURL):
    # This function creates and centers the meme image
    imageStr = urlopen(memeURL).read()
    imageFile = io.BytesIO(imageStr)
    image = pygame.image.load(imageFile)
    # Resizes the image in a frame set by the constants page
    image = aspect_scale(image, constants.imageSize[0], constants.imageSize[1])
    rect = image.get_rect()
    # Gets the outline of the new image and centers it
    rect = rect.move(((constants.screenSize[0]-image.get_size()[0])/2, (constants.screenSize[1]-image.get_size()[1])/2))
    screen.blit(image, rect)


def goForward():
    global activeMemeNum
    if activeMemeNum+1 <= len(memeHistory)-1:
        activeMemeNum += 1
        newMeme = memeHistory[activeMemeNum]
        displayText(memeCaptionHistory[activeMemeNum], constants.titleFontSize, 50, "title")
        displayText("By " + memeAuthorHistory[activeMemeNum], int(constants.titleFontSize/1.5), 85, "author")
        displayNum(20)
        initMeme(newMeme)
        pygame.display.flip()


def goBack():
    global activeMemeNum
    if activeMemeNum-1 >= 0:
        activeMemeNum -= 1
        newMeme = memeHistory[activeMemeNum]
        displayText(memeCaptionHistory[activeMemeNum], constants.titleFontSize, 50, "title")
        displayText("By " + memeAuthorHistory[activeMemeNum], int(constants.titleFontSize/1.5), 85, "author")
        displayNum(20)
        initMeme(newMeme)
        pygame.display.flip()


def displayText(text, fontSize, yPos, type):
    # type refers to whether or not a title, author, etc is being displayed
    if type == "title":
        screen.fill(constants.backgroundColor)
    myfont = pygame.font.SysFont(constants.font, fontSize)
    display = myfont.render(text, True, (0, 0, 0))
    textRect = display.get_rect()
    textRect = textRect.move(((constants.screenSize[0]-display.get_size()[0])/2), yPos)
    screen.blit(display, textRect)


def displayNum(fontSize):
    myfont = pygame.font.SysFont(constants.font, fontSize)
    display = myfont.render("Meme number: " + str(activeMemeNum+1), True, (0, 0, 0))
    textRect = display.get_rect()
    textRect = textRect.move((10, 10))
    screen.blit(display, textRect)


def gameMain():
    global screen, activeMemeNum
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(constants.screenSize)
    screen.fill(constants.backgroundColor)
    gameQuit = False
    createNewMeme()
    autoPlay = False
    while not gameQuit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameQuit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if activeMemeNum+1 <= len(memeHistory)-1:
                        goForward()
                    else:
                        createNewMeme()
                if event.key == pygame.K_LEFT:
                    goBack()
            #     if event.key == pygame.K_SPACE:
            #         if autoPlay:
            #             autoPlay = False
            #         else:
            #             autoPlay = True
            # if autoPlay:
            #     if activeMemeNum+1 <= len(memeHistory)-1:
            #         goForward()
            #         time.sleep(3)
            #     else:
            #         createNewMeme()
            #         time.sleep(3)
    pygame.quit()
    exit()


if __name__ == '__main__':
    gameMain()
