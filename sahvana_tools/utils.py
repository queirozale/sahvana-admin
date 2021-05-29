import requests
import os

IMGBB_API_KEY = os.environ['IMGBB_API_KEY']

def save_image_imgbb(img):
    img = img.split('base64,')[1]
    img = img.encode("utf-8")

    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": img,
    }
    res = requests.post(url, payload)
    img_url = res.json()['data']['url']

    return img_url


def get_images_url(images):
    images_url = []
    for img in images:
        if img != None:
            img_url = save_image_imgbb(img[0])
            images_url.append(img_url)

    return images_url