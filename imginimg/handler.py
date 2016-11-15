#encoding:utf8
__author__='alberto.rincon@beeva.com'

"""
Inserts an image into another
"""

from chalice import Chalice

import json
import urllib
import sys
from py_bing_search import PyBingImageSearch
import logging
from PIL import Image, ImageDraw

logging.basicConfig(level=logging.DEBUG)
BING_API_CREDENTIALS = open('secret').read()

def bing_search(search_term):
    """
    Given a search query, saves the best match into backgroud.extesion file
    :param: search_term. Query for bing api
    """
    background = 'examples/eiffel.png'
    try:
        bing_image = PyBingImageSearch(BING_API_CREDENTIALS, search_term)
        result = bing_image.search(limit=1, format='json')[0]
        extension = result.content_type.split('/')[1]
        urllib.urlretrieve(result.media_url, "background.%s"%extension)
    except Exception as e:
        logging.error(e)
    return background


def selfie(bot,background):
    """
    """
    im_bot = Image.open()
    im_backg = Image.open(sys.argv[2])
    back_x, back_y = im_backg.size

    im_bot = im_bot.resize((back_x/3, back_y/2))

    im_backg.paste(im_bot, (back_x/8, back_y/2), im_bot)

    im_backg.save('output.png', 'PNG')
