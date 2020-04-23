import datetime
import gzip
import os
import networkx as nx
from bz2 import BZ2File as bzopen
from dateutil.relativedelta import *

from data import AS_LINKS_DATA_DIR, AS_REL_DATA_DIR, download_as_links_files, download_as_links_files, download_as_rel_file


class IPv6Graph:
    def __init__(self, start_date, end_date):
        self.G = nx.Graph()
        self.start_date = start_date
        self.end_date = end_date
        self.ipv6_nodes = set()

    def update_relationships(self, year, month):
        fname = os.path.join(AS_REL_DATA_DIR, f'{year}{month}01.as-rel.txt.bz2')
        if not os.path.exists(fname):
            return
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
                    if relationship_type == -1:
                        r = 'c2p'
                    elif relationship_type == 0:
                        r = 'p2p'
                    else:
                        raise Exception('Invalid relationship type!')
                    if (as1, as2) not in self.G.edges:
                        self.G.add_edge(as1, as2, label=r, timestamp=datetime.date(year=int(year), month=int(month), day=1))

    def mark_adopted(self, as_, cur_date):
        self.G.nodes[as_]['ipv6'] = True
        self.G.nodes[as_]['time_adopted'] = cur_date
        neighbors = list(self.G.neighbors(as_))
        ipv6_neighbors = list(filter(lambda x: self.G.nodes[x].get('ipv6') and self.G.nodes[x].get('time_adopted') < cur_date,
            neighbors))
        self.G.nodes[as_]['ipv6_neighbors'] = ipv6_neighbors
        num_neighbors = len(neighbors)
        self.G.nodes[as_]['num_neighbors'] = num_neighbors
        if len(ipv6_neighbors) > 0:
            ipv6_neighbor_times_adopted = [self.G.nodes[x].get('time_adopted') for x in ipv6_neighbors]
            self.G.nodes[as_]['neighbor_last_adopted'] = max(ipv6_neighbor_times_adopted)

    def parse_as_links_file(self, fname, cur_date):
        with gzip.open(fname, 'r') as f:
            for i, line in enumerate(f):
                line = line.decode('utf-8').strip()
                if line.startswith('D') or line.startswith('I'):
                    line = line.split('\t')
                    # type_ = line[0]
                    as1_list = line[1].split(',')
                    as2_list = line[2].split(',')
                    for as1 in as1_list:
                        as1 = int(as1)
                        if as1 not in self.ipv6_nodes:
                            if as1 not in self.G.nodes:
                                continue
                            self.ipv6_nodes.add(as1)
                            self.mark_adopted(as1, cur_date)
                        for as2 in as2_list:
                            as2 = int(as2)
                            if as2 not in self.G.nodes:
                                continue
                            if as2 not in self.ipv6_nodes:
                                self.ipv6_nodes.add(as2)
                                self.mark_adopted(as2, cur_date)

    def build_graph(self):
        ipv6_nodes_monthly = {}
        cur_date = self.start_date
        while cur_date < self.end_date:
            cur_month = cur_date.strftime('%m')
            cur_year = cur_date.strftime('%Y')
            print(f'{cur_month}/{cur_year}')

            download_as_links_files(cur_year, cur_month)
            download_as_rel_file(cur_year, cur_month)

            self.update_relationships(cur_year, cur_month)

            folder = os.path.join(AS_LINKS_DATA_DIR, cur_year + cur_month)
            fnames = sorted(os.listdir(folder))
            for fname in fnames:
                if not fname.endswith('.gz'):
                    continue
                fname_ = os.path.join(folder, fname)
                self.parse_as_links_file(fname_, cur_date)
            print('# IPv6 nodes: ', len(self.ipv6_nodes))
            ipv6_nodes_monthly[cur_date] = len(self.ipv6_nodes)
            cur_date += relativedelta(months=+1)
        return ipv6_nodes_monthly

    def calculate_cascade_size(self, node, seen_nodes):
        time_adopted = self.G.nodes[node]['time_adopted']
        cascade_size = 1
        for neighbor in self.G.neighbors(node):
            if self.G.nodes[neighbor].get('ipv6'):
                neighbor_time_adopted = self.G.nodes[neighbor]['time_adopted']
                if neighbor_time_adopted > time_adopted and neighbor not in seen_nodes:
                    seen_nodes.add(neighbor)
                    cascade_size += self.calculate_cascade_size(neighbor, seen_nodes)
        return cascade_size

    def calculate_cascade_depth(self, node, depth, seen_nodes):
        time_adopted = self.G.nodes[node]['time_adopted']
        max_depth = 0
        for neighbor in self.G.neighbors(node):
            if self.G.nodes[neighbor].get('ipv6'):
                neighbor_time_adopted = self.G.nodes[neighbor]['time_adopted']
                if neighbor_time_adopted > time_adopted and neighbor not in seen_nodes:
                    seen_nodes.add(neighbor)
                    neighbor_depth = self.calculate_cascade_depth(neighbor, depth + 1, seen_nodes)
                    if neighbor_depth > max_depth:
                        max_depth = neighbor_depth
        return max_depth + 1
