# -*- coding: utf-8 -*-
"""
Created on Tue May 12 13:11:23 2020

@author: Sean
"""

import re
import numpy as np
import pandas as pd
from ..utilities.web_browsing import make_soup

base_url = "https://electricbikereview.com/category/bikes/"

all_specs = {
        "make":{
            "num":False
        },
        "model":{
            "num":False
        },
        "price":{
            "num":True,
            "units":"$"
        },
        "total_weight":{
            "num":True,
            "units":"lbs"
        },
        "motor_nominal_output":{
            "num":True,
            "units":"W"
        },
        "estimated_min_range":{
            "num":True,
            "units":"miles"
        },
        "estimated_max_range":{
            "num":True,
            "units":"miles"
        },
        "battery_watt_hours":{
            "num":True,
            "units":"wh"
        },
}
        
def generate_url(base, page):
    """"""
    if page == 1:
        return base
    else:
        return base + "page/" + str(page) + "/"
    
def find_numbers(val):
    """"""
    return [float(re.sub("\$|\,","",i)) for i in val.split()
            if re.sub("\.|\$|\,","",i).isdigit()]
    
def find_products(soup):
    """"""
    pattern = "href=\"(.*?)\""
    
    results = soup.find_all(href=re.compile("https://"),
                            title=re.compile("Review"))
    if results is not None:
        urls = []
        for r in results:
            rs = str(r)
            if "post-thumb-small" in rs:
                url = re.search(pattern, rs).group(1)
                urls.append(url)
                
        return urls
    return []

def find_specs(url, index=0):
    """"""
    
    # Generate the dataframe for this product
    product = pd.DataFrame(np.nan, index=[index], columns=all_specs)
    
    soup = make_soup(url)
    print(url)
    spec_results = soup.find_all("h4")
    for spec_name, dets in all_specs.items():
        spec = spec_name.replace("_","").lower()
        for sr in spec_results:
            srs = str(sr).replace(" ","").lower()
            if spec in srs:
                spec_str = str(sr.next_sibling)
                spec_val = re.sub(
                        "<span>|\n|\t|</span>", "", spec_str).replace(" ","")
                if dets['num']:
                    numbers = find_numbers(spec_val)
                    if numbers:
                        spec_val = numbers[0]
                    else:
                        print(spec_name)
                        print(spec_val)
                        spec_val = np.nan
                product[spec_name] = spec_val
                break
    return product

def compile_product_specs(n_pages=1, pages=None):
    """"""

    all_products = []
    
    if pages is not None:
        pages_to_search = pages
    else:
        pages_to_search = range(n_pages)
        
    for pgi in pages_to_search:
        pg_num = pgi + 1
        soup = make_soup(generate_url(base_url, pg_num))
        urls_for_page = find_products(soup)
        all_products.extend(urls_for_page)
    
    full_specs = pd.DataFrame(columns=all_specs)
    for pi, product in enumerate(all_products):
        full_specs = full_specs.append(find_specs(product, index=pi))
        
    full_specs['url'] = all_products
    return full_specs

