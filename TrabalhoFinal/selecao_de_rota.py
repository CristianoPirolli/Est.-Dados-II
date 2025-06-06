def selecionar_melhor_rota(lista_de_rotas, criterios_de_prioridade):
    if not lista_de_rotas:
        return None

    def chave_de_ordenacao(rota):
        valores_chave = []
        for criterio, objetivo in criterios_de_prioridade:
            valor = rota.get(criterio)
            if valor is None:
                valor = float('inf') if objetivo == 'min' else float('-inf')
            if objetivo == 'max':
                valor = -valor
            valores_chave.append(valor)
        return tuple(valores_chave)
    rotas_ordenadas = sorted(lista_de_rotas, key=chave_de_ordenacao)
    return rotas_ordenadas[0] if rotas_ordenadas else None