import kruncher.utils as utils

import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":

    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    # url = "https://siecledigital.fr/2017/04/18/comment-influencer-le-referencement-naturel-grace-son-nom-de-domaine/"
    # web_page = requests.get(url, headers=headers)
    # soup = BeautifulSoup(web_page.content, "html.parser")
    #
    # out_text= utils.extractTextFromPage(soup,"div","class","post-content description ","p")
    # print("+--> Text : "+ out_text)
    # print("+--> Text : {}".format(len(out_text.split())))
    #
    # out_img= utils.extractImageFromPage(soup,"div","class","featured","a","href")
    # print("+--> Image : "+ out_img)


    url="https://www.sciencesetavenir.fr/high-tech/drones/video-qu-advient-il-lorsqu-un-drone-est-frappe-par-la-foudre_112261"
    web_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_page.content, "html.parser")
    out_img= utils.extractImageFromPage(soup,"div","class","article-image","img","data-src")
    print("+--> Image : "+ out_img)
