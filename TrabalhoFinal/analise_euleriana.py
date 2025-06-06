from graph import Graph
import collections

# --- Funções para Caminho/Circuito Euleriano ---

def obter_graus_vertices(grafo_obj: Grafo) -> collections.defaultdict:
    graus = collections.defaultdict(int)
    for vertice in grafo_obj.obter_vertices():
        graus[vertice] = len(grafo_obj.obter_vizinhos(vertice))
    return graus

def tem_caminho_euleriano(grafo_obj: Grafo) -> bool:
    if not grafo_obj.obter_vertices():
        return False
    tem_arestas = False
    for v in grafo_obj.obter_vertices():
        if grafo_obj.obter_vizinhos(v):
            tem_arestas = True
            break
    if not tem_arestas and len(grafo_obj.obter_vertices()) > 1:
        return False
    if not tem_arestas and len(grafo_obj.obter_vertices()) == 1:
        return True


    graus = obter_graus_vertices(grafo_obj)
    contagem_grau_impar = 0
    for vertice in grafo_obj.obter_vertices():
        if graus[vertice] % 2 != 0:
            contagem_grau_impar += 1
    return contagem_grau_impar == 0 or contagem_grau_impar == 2

def tem_circuito_euleriano(grafo_obj: Grafo) -> bool:
    if not grafo_obj.obter_vertices():
        return False

    graus = obter_graus_vertices(grafo_obj)
    if not any(g > 0 for g in graus.values()):
        return False

    for vertice in grafo_obj.obter_vertices():
        if graus[vertice] % 2 != 0:
            return False
    return True