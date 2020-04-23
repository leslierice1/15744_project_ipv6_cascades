import os
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen

AS_REL_PREFIX = 'http://data.caida.org/datasets/as-relationships/serial-1'
AS_LINKS_PREFIX = 'http://data.caida.org/datasets/topology/ark/ipv6/as-links'
AS_REL_DATA_DIR = 'as_relationships_data'
AS_LINKS_DATA_DIR = 'as_links_data'

def download_as_links_files(year, month):
    url = f'{AS_LINKS_PREFIX}/{year}/{month}'
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    ark_monitors = set()
    for link in soup.find_all('a'):
        l = link.get('href')
        if l.startswith('cycle-aslinks.l8') and year + month in l:
            lsplit = l.split('.')
            m = lsplit[-3]
            if m not in ark_monitors:
                links.append(l)
                ark_monitors.add(m)
    if not os.path.exists(AS_LINKS_DATA_DIR):
        os.mkdir(AS_LINKS_DATA_DIR)
    out_dir = os.path.join(AS_LINKS_DATA_DIR, year + month)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    for l in links:
        full_link = os.path.join(url, l)
        out_file = os.path.join(out_dir, l)
        if os.path.exists(out_file):
            continue
        else:
            print(f'Downloading {full_link} to {out_file}')
            try:
                urllib.request.urlretrieve(full_link, out_file)
            except:
                print('Failed to download!')


def download_as_rel_file(year, month):
    l = f'{year}{month}01.as-rel.txt.bz2'
    full_link = f'{AS_REL_PREFIX}/{l}'
    if not os.path.exists(AS_REL_DATA_DIR):
        os.mkdir(AS_REL_DATA_DIR)
    out_file = os.path.join(AS_REL_DATA_DIR, l)
    if not os.path.exists(out_file):
        print(f'Downloading {full_link} to {out_file}')
        try:
            urllib.request.urlretrieve(full_link, out_file)
        except:
            print('Failed to download!')
