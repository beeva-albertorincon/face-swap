"""
AWS Lambda for BuyBot image combination
"""
from chalice import Chalice

app = Chalice(app_name='imginimg')
app.debug = True

"""
Utils
"""
import json
import urllib
import sys
import logging
import boto3

from datetime import datetime
from py_bing_search import PyBingImageSearch
from PIL import Image, ImageDraw

logging.basicConfig(level=logging.INFO)
BING_API_CREDENTIALS = str(open('secret.py').readline())

# logging.info('using credentials %s' %BING_API_CREDENTIALS)
DEFAULT_FOREGROUND = 'examples/bot.png'

def bing_search(search_term):
    """
    Given a search query, saves the best match into backgroud.extesion file
    :param: search_term. Query for bing api
    """
    background = 'examples/eiffel.png'
    try:
        bing_image = PyBingImageSearch(BING_API_CREDENTIALS.strip(), search_term)
        result = bing_image.search(limit=1, format='json')[0]
        extension = result.content_type.split('/')[1]
        urllib.urlretrieve(result.media_url, "/tmp/background.%s"%extension)
        background = "/tmp/background.%s"%extension
        logging.info('Bing search succesful')
    except Exception as e:
        logging.error(e)
    return background


def combine_images(foreground,background):
    """
    Given two images, overlaps the first into the second.
    """
    combined = 'examples/output.png'
    try:
        im_bot = Image.open(foreground)
        im_backg = Image.open(background)
        back_x, back_y = im_backg.size
        im_bot = im_bot.resize((back_x/3, back_y/2))
        im_backg.paste(im_bot, (back_x/8, back_y/2), im_bot)
        im_backg.save('/tmp/output.png', 'PNG')
        combined = '/tmp/output.png'
        logging.info('Done combine images')
    except Exception as e:
        logging.error(e)
    return combined

"""
Routes
"""
@app.route('/selfie/{query}')
def selfie(query):
    """
    Inserts the default image into the one found by using the query passed as parameter.
    """
    background = bing_search(query)
    combined = combine_images(DEFAULT_FOREGROUND, background)
    s3_client = boto3.client('s3')
    bucket_url = 'https://s3-eu-west-1.amazonaws.com/beeva-radical-lab/lambdas/botselfie/'
    url = '%s%s' %(bucket_url, 'default.png')
    try:
        now = '%s%s%s%s%s%s%s' %(datetime.now().year,datetime.now().month,datetime.now().day,datetime.now().hour,datetime.now().min,datetime.now().second,datetime.now().microsecond)
        now = hash(now)
        filename = 'combined%s.png' %now
        s3_client.upload_file(combined, 'beeva-radical-lab', 'lambdas/botselfie/%s' %filename, ExtraArgs={'ACL': 'public-read'})
        url = '%s%s' %(bucket_url,filename)
    except Exception as e:
        logging.error(e)
    return {'res': url}
