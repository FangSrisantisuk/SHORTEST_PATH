from typing import List, Tuple
from itertools import product

INF = 1e99


class Graph:

    def __init__(
            self,
            vertices: List[Tuple[str, int]],
            edges: List[Tuple[str, str, int]]
    ) -> None:
        self.vertices = vertices
        self._edges = edges
        self._connections = {}

        # Set relationship
        for (src, dst, cost) in self._edges:
            if src not in self._connections:
                self._connections[src] = {}
            if dst not in self._connections[src]:
                self._connections[src][dst] = cost

    def __getitem__(self, item: str | Tuple[str, str]):
        if isinstance(item, str):
            return self._connections.get(item, None)
        if isinstance(item, tuple):
            assert len(item) == 2, "item must be (src, dst)"
            assert any(item[0] == vertex[0] for vertex in self.vertices), f"src node: {item[0]} must be defined"
            assert any(item[1] == vertex[0] for vertex in self.vertices), f"src node: {item[1]} must be defined"
            
            # assert item[0] in self.vertices, f"src node: {item[0]} must be defined"
            # assert item[1] in self.vertices, f"dst node: {item[1]} must be defined"
            key_dict = self._connections.get(item[0], None)
            if key_dict is not None:
                return key_dict.get(item[1], INF)
            return None

    def neighbour(self, node: str):
        if self[node]:
            return list(self[node].keys())
        return []
    
    def get_device_cost(self,device_name:str)->int:
        cost = [v[1] for v in self.vertices if v[0] == device_name]
        return cost[0]


def k_shortest_path(G: Graph, src: str, dst: str | list[str], K: int):
    result = {dest: [] for dest in dst}
    count = {vertice[0]: 0 for vertice in G.vertices}
    priority_queue = [{"path": [src], "cost": 0, "dst": src}]

    while len(priority_queue) != 0 and sum([count[dest] for dest in dst]) < K * len(dst):
        priority_queue = sorted(priority_queue, key=lambda x: x['cost'])
        path = priority_queue.pop(0)
        u = path['dst']
        count[u] += 1
        if u in dst:
            path['cost'] = path['cost'] - G.get_device_cost(u)
            result[u].append(path)
        if count[u] < K:
            for v in G.neighbour(u):
                pv = {"path": path['path'] + [v],
                      "cost": path['cost'] + G[u, v] + G.get_device_cost(v),
                      "dst": v
                      }
                priority_queue.append(pv)
    return result


def find_shared_nodes (subpaths):
    set_path = [set(subpath[1:]) for subpath in subpaths]
    shared_nodes = set_path[0].intersection(*set_path[1:])
    output = list (shared_nodes)
    return output

def find_shared_edges (subpaths):
    shared_edges = []

    for i in range(len(subpaths[0]) - 1):
        edge1 = (subpaths[0][i], subpaths[0][i+1])
        for j in range(len(subpaths[1]) - 1):
            edge2 = (subpaths[1][j], subpaths[1][j+1])
            if edge1 == edge2:
                shared_edges.append(edge1)
    return shared_edges

def cal_nodes_cost (G: Graph, shared_nodes):
    cost = 0

    if len(shared_nodes) == 0:
        return cost
    
    for i in range(len(shared_nodes)):
        cost += G.get_device_cost(shared_nodes[i])
    return cost

def cal_edges_cost (G: Graph, shared_edges):
    cost = 0

    if len(shared_edges) == 0:
        return cost

    for i in range(len(shared_edges)):
        cost += G[shared_edges[i]]
    return cost

def multilple_dest_path (G: Graph, result, K: int):
    lists = list (result.values())
    combinations = list (product(*lists))
    output = []

    for combi in combinations:
        list_of_paths = [item["path"] for item in combi]

        shared_nodes = find_shared_nodes (list_of_paths)
        shared_edges = find_shared_edges (list_of_paths)
        
        overall_cost = 0
        list_of_costs = [item["cost"] for item in combi]
        for cost in list_of_costs:
            overall_cost += + cost 
        overall_cost = overall_cost - cal_nodes_cost(G,shared_nodes) - cal_edges_cost(G,shared_edges)

        part_of_output = {"subpaths": combi, "shared_devices": shared_nodes, "shared_connections": shared_edges, "overall_cost": overall_cost}
        output.append(part_of_output)

    output = sorted(output, key=lambda x: x["overall_cost"])

    if len(output) > K:
        output = output[:K]

    return output