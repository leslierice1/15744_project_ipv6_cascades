import argparse
import json
import os
import urllib.request
import gzip
from bs4 import BeautifulSoup
import networkx as nx
from networkx.readwrite import json_graph
from urllib.request import urlopen


def parse_data(G, data_dir):
    not_in_graph_count = 0
    for fname in os.listdir(data_dir):
        if not fname.endswith('.gz'):
            continue
        with gzip.open(os.path.join(data_dir, fname), 'r') as f:
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
                            if G.has_edge(as1, as2):
                                G[as1][as2]['ipv6'] = True
                            else:
                                # print(type_)
                                not_in_graph_count += 1
    print('not in graph', not_in_graph_count)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', type=str, help='Example format: 12-01-2018', default='01-01-2019')
    parser.add_argument('--end-date', type=str, default='02-01-2019')
    parser.add_argument('--data-dir', type=str, default='as_links_data')
    parser.add_argument('--as-relationships-data', type=str, default='as_relationships_data.json')
    return parser.parse_args()


def main():
    args = get_args()
    start_month, start_day, start_year = args.start_date.split('-')
    identifier = start_year + start_month + start_day
    print(identifier)
    ASLinks = nx.Graph()
    start_url = f'http://data.caida.org/datasets/topology/ark/ipv6/as-links/{start_year}/{start_month}'
    print(start_url)
    html = urlopen(start_url)
    soup = BeautifulSoup(html, 'html.parser')
    # print(soup.prettify())
    links = []
    for link in soup.find_all('a'):
        l = link.get('href')
        if l.startswith('cycle-aslinks.l8') and identifier in l:
            links.append(l)
    print(links)

    out_dir = os.path.join('as_links_data', identifier)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    for l in links:
        full_link = os.path.join(f'http://data.caida.org/datasets/topology/ark/ipv6/as-links/{start_year}/{start_month}/', l)
        print(full_link)
        urllib.request.urlretrieve(full_link, os.path.join(out_dir, l))

    # parse_data(G, args.data_dir)
    #
    # ipv6_count = 0
    # no_data_count = 0
    # for edge in G.edges:
    #     if G.edges[edge].get('ipv6'):
    #         ipv6_count += 1
    #     else:
    #         no_data_count += 1
    # print(ipv6_count)
    # print(no_data_count)

if __name__ == "__main__":
    main()
