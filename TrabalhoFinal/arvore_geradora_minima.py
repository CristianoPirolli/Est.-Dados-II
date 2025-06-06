from grafo import Grafo
import heapq

class DSU:
    def __init__(self, vertices):
        self.pai = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def encontrar(self, item):
        if self.pai[item] == item:
            return item
        self.pai[item] = self.encontrar(self.pai[item])
        return self.pai[item]

    def unir(self, raiz_conjunto1, raiz_conjunto2):
        if self.rank[raiz_conjunto1] < self.rank[raiz_conjunto2]:
            self.pai[raiz_conjunto1] = raiz_conjunto2
        elif self.rank[raiz_conjunto1] > self.rank[raiz_conjunto2]:
            self.pai[raiz_conjunto2] = raiz_conjunto1
        else:
            self.pai[raiz_conjunto2] = raiz_conjunto1
            self.rank[raiz_conjunto1] += 1

def kruskal(grafo_obj: Grafo):
    agm = []
    custo_total = 0
    arestas = []

    pares_processados = set()
    for u in grafo_obj.obter_vertices():
        for info_aresta in grafo_obj.obter_vizinhos(u):
            v = info_aresta['node']
            peso = info_aresta['weight']
            if tuple(sorted((u, v))) not in pares_processados:
                arestas.append((peso, u, v))
                pares_processados.add(tuple(sorted((u,v))))
    arestas.sort()
    
    dsu = DSU(grafo_obj.obter_vertices())
    
    for peso, u, v in arestas:
        if dsu.encontrar(u) != dsu.encontrar(v):
            dsu.unir(dsu.encontrar(u), dsu.encontrar(v))
            agm.append({'u': u, 'v': v, 'weight': peso})
            custo_total += peso