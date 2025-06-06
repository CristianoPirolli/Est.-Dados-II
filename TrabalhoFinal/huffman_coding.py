import heapq
import collections

class NoHuffman:
    def __init__(self, caractere, frequencia):
        self.caractere = caractere
        self.frequencia = frequencia
        self.esquerda = None
        self.direita = None

    def __lt__(self, outro_no):
        return self.frequencia < outro_no.frequencia

def construir_tabela_frequencia(string_dados):
    if not string_dados:
        return collections.Counter()
    return collections.Counter(string_dados)

def construir_arvore_huffman(tabela_frequencia):
    if not tabela_frequencia:
        return None

    fila_prioridade = [NoHuffman(caractere, freq) for caractere, freq in tabela_frequencia.items()]
    heapq.heapify(fila_prioridade)

    while len(fila_prioridade) > 1:
        filho_esquerda = heapq.heappop(fila_prioridade)
        filho_direita = heapq.heappop(fila_prioridade)

        frequencia_combinada = filho_esquerda.frequencia + filho_direita.frequencia
        no_mesclado = NoHuffman(None, frequencia_combinada)
        no_mesclado.esquerda = filho_esquerda
        no_mesclado.direita = filho_direita

        heapq.heappush(fila_prioridade, no_mesclado)

    return fila_prioridade[0] if fila_prioridade else None

def gerar_codigos_huffman(raiz_arvore, codigo_atual="", mapa_codigos=None):
    if mapa_codigos is None:
        mapa_codigos = {}

    if raiz_arvore is None:
        return mapa_codigos

    if raiz_arvore.caractere is not None:
        mapa_codigos[raiz_arvore.caractere] = codigo_atual or "0"
        return mapa_codigos

    gerar_codigos_huffman(raiz_arvore.esquerda, codigo_atual + "0", mapa_codigos)
    gerar_codigos_huffman(raiz_arvore.direita, codigo_atual + "1", mapa_codigos)
    
    return mapa_codigos

def codificar_huffman(string_dados, mapa_codigos_huffman):
    """Codifica a string de dados usando os códigos de Huffman gerados."""
    if not string_dados or not mapa_codigos_huffman:
        return ""
        
    string_codificada = "".join([mapa_codigos_huffman.get(caractere, "") for caractere in string_dados])
    return string_codificada

def decodificar_huffman(dados_codificados, raiz_arvore_huffman):
    """Decodifica dados comprimidos (string de bits) usando a árvore de Huffman."""
    if not dados_codificados or raiz_arvore_huffman is None:
        return ""

    string_decodificada = []
    no_atual = raiz_arvore_huffman

    if no_atual.esquerda is None and no_atual.direita is None and no_atual.caractere is not None:
        if all(bit == (gerar_codigos_huffman(raiz_arvore_huffman).get(no_atual.caractere) or "0")[0] for bit in dados_codificados):
             return no_atual.caractere * len(dados_codificados)
        else:
            return "Erro: Dados codificados inválidos para árvore de um único nó."


    for bit in dados_codificados:
        if bit == '0':
            no_atual = no_atual.esquerda
        elif bit == '1':
            no_atual = no_atual.direita
        else:
            continue

        if no_atual is None:
            return "Erro: Sequência de bits inválida durante decodificação."

        if no_atual.caractere is not None:
            string_decodificada.append(no_atual.caractere)
            no_atual = raiz_arvore_huffman
            
    return "".join(string_decodificada)