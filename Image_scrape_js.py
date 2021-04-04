from requests_html import HTMLSession
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse

import os

'''Note! This is made for jvascript-loaded data on websites. For others,
this script would have to be rewritten without having to initialise a JS session.
It would also remove the need for importing requests_html. '''

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_images(url):
    """
    Returns all image URLs on a single `url`
    """
    # initialise the session
    session = HTMLSession()
    # make the HTTP request and retrieve response
    response = session.get(url)
    # execute Javascript
    response.html.render()
    # construct the soup parser
    soup = bs(response.html.html, "html.parser")
    urls = []
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src") or img.attrs.get("data-src")
        if not img_url:
            # if img does not contain src attribute, just skip
            continue
        # make the URL absolute by joining domain with the URL that is just extracted
        img_url = urljoin(url, img_url)
        # remove URLs like '/hsts-pixel.gif?c=3.2.5'
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        # finally, if the url is valid
        if is_valid(img_url):
            urls.append(img_url)
    # close the session to end browser process
    session.close()
    return urls


def download(url, pathname):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))

    # get the file name
    filename = os.path.join(pathname, url.split("/")[-1])

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", 
    total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))


def main(url, path):
    # get all images
    imgs = get_all_images(url)
    for img in imgs:
        # for each img, download it
        download(img, path)
    
    
'''Execute function with input: "url of page", "folder path" (by default placed in
 parent of current directory). '''

main("https://www.planespotters.net/photo/search?reg=&airline=Emirates&act"\
    "ype=t_747&searchtext=&searchtype=photographer&s=hq", "Emirates")