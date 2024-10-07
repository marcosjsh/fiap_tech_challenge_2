from values import *
from helper import gerar_coordenadas_demandas_clientes, plotar_rotas
from scipy.spatial.distance import cdist
import numpy as np

def algoritmo_clarke_and_wright(numero_veiculos, capacidade_veiculo, clientes_coordenadas, clientes_demandas):
    # Coordenadas completas (depósito + clientes)
    deposito_coordenadas = np.array([[0, 0]])  # Coordenadas do depósito
    todas_coordenadas = np.vstack([deposito_coordenadas, clientes_coordenadas])

    # Matriz de distâncias
    matriz_distancias = cdist(todas_coordenadas, todas_coordenadas)

    # Tamanho da matriz (número total de nós)
    tamanho_matriz = len(matriz_distancias)

    # Inicializar rotas individuais para cada cliente
    rotas = []
    for i in range(1, tamanho_matriz):
        rotas.append([0, i, 0])  # Rota do depósito ao cliente e de volta

    # Cálculo das economias (savings)
    savings = []
    for i in range(1, tamanho_matriz):
        for j in range(i+1, tamanho_matriz):
            saving = matriz_distancias[0][i] + matriz_distancias[0][j] - matriz_distancias[i][j]
            savings.append((saving, i, j))

    # Ordenar as economias em ordem decrescente
    savings.sort(reverse=True)

    # Dicionário para rastrear em qual rota cada cliente está
    rota_de_cliente = {i: i-1 for i in range(1, tamanho_matriz)}

    # Capacidades das rotas
    capacidades_rotas = [clientes_demandas[i-1] for i in range(1, tamanho_matriz)]

    # Aplicar as economias para combinar rotas
    for saving, i, j in savings:
        rota_i = rota_de_cliente[i]
        rota_j = rota_de_cliente[j]

        if rota_i != rota_j and rotas[rota_i] and rotas[rota_j]:
            # Verificar se não excede a capacidade do veículo
            demanda_total = capacidades_rotas[rota_i] + capacidades_rotas[rota_j]
            if demanda_total <= capacidade_veiculo:
                # Verificar se i está no final da sua rota e j no início da sua rota
                if rotas[rota_i][-2] == i and rotas[rota_j][1] == j:
                    # Combinar as rotas
                    nova_rota = rotas[rota_i][:-1] + rotas[rota_j][1:]
                    rotas[rota_i] = nova_rota
                    rotas[rota_j] = []
                    # Atualizar a capacidade da rota
                    capacidades_rotas[rota_i] = demanda_total
                    capacidades_rotas[rota_j] = 0
                    # Atualizar o mapeamento dos clientes para a nova rota
                    for cliente in rotas[rota_i]:
                        if cliente != 0:
                            rota_de_cliente[cliente] = rota_i

                # Verificar se j está no final da sua rota e i no início da sua rota
                elif rotas[rota_j][-2] == j and rotas[rota_i][1] == i:
                    # Combinar as rotas
                    nova_rota = rotas[rota_j][:-1] + rotas[rota_i][1:]
                    rotas[rota_j] = nova_rota
                    rotas[rota_i] = []
                    # Atualizar a capacidade da rota
                    capacidades_rotas[rota_j] = demanda_total
                    capacidades_rotas[rota_i] = 0
                    # Atualizar o mapeamento dos clientes para a nova rota
                    for cliente in rotas[rota_j]:
                        if cliente != 0:
                            rota_de_cliente[cliente] = rota_j

    # Remover rotas vazias
    rotas = [rota for rota in rotas if rota]

    # Se o número de rotas exceder o número de veículos, manter apenas as melhores
    if len(rotas) > numero_veiculos:
        print(f"Número de rotas ({len(rotas)}) excede o número de veículos disponíveis ({numero_veiculos}).")
        rotas = rotas[:numero_veiculos]

    # Calcular a distância total
    distancia_total = 0
    for rota in rotas:
        for i in range(len(rota) - 1):
            distancia_total += matriz_distancias[rota[i]][rota[i+1]]

    return rotas, distancia_total, capacidades_rotas, todas_coordenadas

def exibir_resultados(rotas, distancia_total, capacidades_rotas, clientes_demandas):
    print("\nSoluções encontradas pelo Algoritmo de Clarke e Wright:")
    total_carga = 0
    for idx, rota in enumerate(rotas):
        carga_rota = sum([clientes_demandas[cliente - 1] for cliente in rota if cliente != 0])
        total_carga += carga_rota
        print(f"Veículo {idx + 1}: Rota {rota} | Carga: {carga_rota}")
    print(f"\nDistância total percorrida: {distancia_total:.2f} unidades")
    print(f"Carga total transportada: {total_carga}")

if __name__ == '__main__':
    # Gerar ou carregar os dados dos clientes
    clientes_coordenadas, clientes_demandas = gerar_coordenadas_demandas_clientes()

    # Executar o Algoritmo de Clarke e Wright
    rotas, distancia_total, capacidades_rotas, todas_coordenadas = algoritmo_clarke_and_wright(
        numero_veiculos,
        capacidade_veiculo,
        clientes_coordenadas,
        clientes_demandas
    )

    # Exibir os resultados
    exibir_resultados(rotas, distancia_total, capacidades_rotas, clientes_demandas)

    # Visualizar as rotas
    plotar_rotas('Rotas Geradas pelo Algoritmo de Clarke e Wright', rotas, todas_coordenadas).show()
