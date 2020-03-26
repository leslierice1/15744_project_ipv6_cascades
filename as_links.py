import argparse
import json
import os
import urllib.request
import gzip
from bs4 import BeautifulSoup
import networkx as nx
from networkx.readwrite import json_graph
from urllib.request import urlopen


def parse_files(data_dir):
    G = nx.Graph()
    folder = os.path.join('as_links_data', data_dir)
    for fname in os.listdir(folder):
        if not fname.endswith('.gz'):
            continue
        with gzip.open(os.path.join(folder, fname), 'r') as f:
            for i, line in enumerate(f):
                line = line.decode('utf-8').strip()
                if line.startswith('D') or line.startswith('I'):
                    line = line.split('\t')
                    type_ = line[0]
                    as1_list = line[1].split(',')
                    as2_list = line[2].split(',')
                    for as1 in as1_list:
                        as1 = int(as1)
                        for as2 in as2_list:
                            as2 = int(as2)
                            G.add_edge(as1, as2)
    return G


def download_files(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    url = f'http://data.caida.org/datasets/topology/ark/ipv6/as-links/{year}/{month}'
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        l = link.get('href')
        if l.startswith('cycle-aslinks.l8') and date in l:
            links.append(l)

    out_dir = os.path.join('as_links_data', date)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    for l in links:
        full_link = os.path.join(url, l)
        out_file = os.path.join(out_dir, l)
        if os.path.exists(out_file):
            continue
        else:
            print(f'Downloading {full_link}')
        urllib.request.urlretrieve(full_link, out_file)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', type=str, help='Example format: 20181201', default='20181201')
    parser.add_argument('--end-date', type=str, default='20190101')
    parser.add_argument('--data-dir', type=str, default='as_links_data')
    parser.add_argument('--as-relationships-data', type=str, default='as_relationships_data.json')
    return parser.parse_args()


def main():
    if not os.path.exists('as_links_data'):
        os.mkdir('as_links_data')

    args = get_args()

    download_files(args.start_date)
    download_files(args.end_date)

    start_G = parse_files(args.start_date)
    print(f'start G # nodes: {len(start_G.nodes)}')
    print(f'start G # edges: {len(start_G.edges)}')

    end_G = parse_files(args.end_date)
    print(f'end G # nodes: {len(end_G.nodes)}')
    print(f'end G # edges: {len(end_G.edges)}')


if __name__ == "__main__":
    main()
