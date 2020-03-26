import argparse
import json
import os
from bz2 import BZ2File as bzopen

import networkx as nx
from networkx.readwrite import json_graph


class ASRelationships:
    def __init__(self):
        self.G = nx.Graph()

    def add_connection(self, as1, as2, relationship_type):
        if relationship_type == -1:
            # p2c relationship: as1=provider, as2=customer
            # self.G.add_edge(as2, as1, label='c2p')
            pass
        elif relationship_type == 0:
            # p2p relationship
            self.G.add_edge(as1, as2, label='p2p')
            # self.G.add_edge(as2, as1, label='p2p')
        else:
            raise Exception('Invalid relationship type!')

    def parse_as_rel_file(self, fname):
        with bzopen(fname, 'r') as f:
            for i, line in enumerate(f):
                line = line.decode('utf-8').strip()
                if line.startswith('#'):
                    continue
                else:
                    l = line.split('|')
                    as1 = int(l[0])
                    as2 = int(l[1])
                    relationship_type = int(l[2])
                    self.add_connection(as1, as2, relationship_type)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=str, default='as_relationships_data')
    return parser.parse_args()


def main():
    args = get_args()
    as_relationships = ASRelationships()
    for fname in os.listdir(args.data_dir):
        if not fname.endswith('.bz2'):
            continue
        as_relationships.parse_as_rel_file(os.path.join(args.data_dir, fname))
    print(f'# nodes: {len(as_relationships.G.nodes)}')
    print(f'# edges: {len(as_relationships.G.edges)}')
    data = json_graph.node_link_data(as_relationships.G)
    with open('as_relationships_data.json', 'w') as outfile:
        json.dump(data, outfile)


if __name__ == "__main__":
    main()
