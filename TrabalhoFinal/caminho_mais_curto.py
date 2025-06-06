import heapq
import math
from graph import Graph

def dijkstra(graph: Graph, start_node: str, end_node: str):
    """
    Calcula o caminho mais curto entre start_node e end_node usando o algoritmo de Dijkstra.
    Retorna uma tupla (distância_total, caminho_reconstruído).
    Se não houver caminho, retorna (math.inf, []).
    """
    if start_node not in graph.get_vertices() or end_node not in graph.get_vertices():
        print(f"Erro: Nó inicial '{start_node}' ou final '{end_node}' não existe no grafo.")
        return math.inf, []

    distances = {vertex: math.inf for vertex in graph.get_vertices()}
    predecessors = {vertex: None for vertex in graph.get_vertices()}
    distances[start_node] = 0

    priority_queue = [(0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        if current_node == end_node:
            break

        for neighbor_info in graph.get_neighbors(current_node):
            neighbor_node = neighbor_info['node']
            weight = neighbor_info['weight']
            distance_through_current = current_distance + weight

            if distance_through_current < distances[neighbor_node]:
                distances[neighbor_node] = distance_through_current
                predecessors[neighbor_node] = current_node
                heapq.heappush(priority_queue, (distance_through_current, neighbor_node))

    path = []
    current = end_node
    if distances[current] == math.inf:
        return math.inf, []

    while current is not None:
        path.insert(0, current)
        current = predecessors[current]

    if path[0] == start_node:
        return distances[end_node], path
    else:
        return math.inf, []