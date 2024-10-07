from helper import gerar_coordenadas_demandas_clientes, plotar_rotas
from values import *
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import numpy as np

def heuristica_nearest_neighbour(deposito_coordenadas, clientes_coordenadas, clientes_demandas, capacidade_veiculo):
    # Converter capacidade_veiculo para inteiro, se necessário
    if isinstance(capacidade_veiculo, str):
        capacidade_veiculo = int(capacidade_veiculo)

    # Coordenadas completas (depósito + clientes)
    todas_coordenadas = np.vstack([deposito_coordenadas, clientes_coordenadas])
    matriz_distancias = cdist(todas_coordenadas, todas_coordenadas)  # Removida a multiplicação por 1000

    numero_clientes = len(clientes_coordenadas)
    clientes_nao_atendidos = set(range(1, numero_clientes + 1))
    rotas = []

    while clientes_nao_atendidos:
        rota = [0]  # Iniciar rota no depósito
        carga_atual = 0
        cliente_atual = 0  # Começa no depósito

        while True:
            # Encontrar clientes não atendidos que podem ser adicionados
            candidatos = []
            for cliente in clientes_nao_atendidos:
                demanda = clientes_demandas[cliente - 1]
                if carga_atual + demanda <= capacidade_veiculo:
                    distancia = matriz_distancias[cliente_atual][cliente]
                    candidatos.append((distancia, cliente))

            if not candidatos:
                break  # Não há mais clientes que cabem na capacidade restante

            # Selecionar o cliente mais próximo
            candidatos.sort()
            _, cliente_mais_proximo = candidatos[0]

            # Adicionar cliente à rota
            rota.append(cliente_mais_proximo)
            carga_atual += clientes_demandas[cliente_mais_proximo - 1]
            clientes_nao_atendidos.remove(cliente_mais_proximo)
            cliente_atual = cliente_mais_proximo

        rota.append(0)  # Retornar ao depósito
        rotas.append(rota)

    # Calcular a distância total percorrida
    distancia_total = 0
    for rota in rotas:
        for i in range(len(rota) - 1):
            distancia_total += matriz_distancias[rota[i]][rota[i+1]]

    return rotas, distancia_total


if __name__ == '__main__':
    # Dados do problema
    deposito_coordenadas = np.array([[0, 0]])  # Centro do mapa
    clientes_coordenadas, clientes_demandas = gerar_coordenadas_demandas_clientes()

    # Executar a heurística do Nearest Neighbour
    rotas, distancia_total = heuristica_nearest_neighbour(deposito_coordenadas, clientes_coordenadas, clientes_demandas, capacidade_veiculo)

    # Exibir resultados
    print("Soluções encontradas pela Heurística Nearest Neighbour:")
    total_carga = 0
    for idx, rota in enumerate(rotas):
        carga_rota = sum([clientes_demandas[cliente - 1] for cliente in rota if cliente != 0])
        total_carga += carga_rota
        print(f"Veículo {idx + 1}: Rota {rota} | Carga: {carga_rota}")
    print(f"\nDistância total percorrida: {distancia_total:.2f} unidades")
    print(f"Carga total transportada: {total_carga}")

    # Coordenadas completas para plotagem
    todas_coordenadas = np.vstack([deposito_coordenadas, clientes_coordenadas])

    # Visualizar as rotas
    plotar_rotas('Rotas Geradas pela Heurística do Vizinho Mais Próximo', rotas, todas_coordenadas)
