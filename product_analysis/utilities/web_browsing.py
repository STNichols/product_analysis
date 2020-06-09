# -*- coding: utf-8 -*-
"""
Created on Tue May 12 13:11:23 2020

@author: Sean
"""

import requests
from bs4 import BeautifulSoup

def make_soup(url):
    """"""
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")