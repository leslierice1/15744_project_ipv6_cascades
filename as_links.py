import argparse
import json
import os
import gzip

from networkx.readwrite import json_graph

def parse_data(G, data_dir):
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

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=str, default='as_links_data')
    parser.add_argument('--as-relationships-data', type=str, default='as_relationships_data.json')
    return parser.parse_args()


def main():
    args = get_args()
    with open(args.as_relationships_data) as json_file:
        as_relationships_data = json.load(json_file)
    G = json_graph.node_link_graph(as_relationships_data)

    parse_data(G, args.data_dir)

    ipv6_count = 0
    no_data_count = 0
    for edge in G.edges:
        if G.edges[edge].get('ipv6'):
            ipv6_count += 1
        else:
            no_data_count += 1
    print(ipv6_count)
    print(no_data_count)

if __name__ == "__main__":
    main()
