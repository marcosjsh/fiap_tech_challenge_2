from values import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import os


def gerar_coordenadas_demandas_clientes():
    if os.path.exists(COORDENADAS_CLIENTES_FILE) and os.path.exists(DEMANDAS_CLIENTES_FILE):
        print("Carregando dados dos clientes a partir dos arquivos...")
        clientes_coordenadas = pd.read_csv(COORDENADAS_CLIENTES_FILE).values
        clientes_demandas = pd.read_csv(DEMANDAS_CLIENTES_FILE)['demand'].values
        return clientes_coordenadas, clientes_demandas

    print("Arquivos não encontrados. Gerando novos dados aleatórios...")
    np.random.seed(random_seed)
    random.seed(random_seed)

    clientes_coordenadas = np.random.uniform(0, 100, size=(numero_clientes, 2))
    clientes_demandas = np.random.randint(lote_minimo, lote_maximo + 1, size=numero_clientes)

    df_coords = pd.DataFrame(clientes_coordenadas, columns=['x', 'y'])
    df_coords.to_csv(COORDENADAS_CLIENTES_FILE, index=False)

    df_demands = pd.DataFrame({'demand': clientes_demandas})
    df_demands.to_csv(DEMANDAS_CLIENTES_FILE, index=False)

    print("Dados salvos nos arquivos.")

    return clientes_coordenadas, clientes_demandas


def plotar_rotas(titulo, rotas, todas_coordenadas, corrigir_sequencia=False):
    plt.figure(figsize=(12, 8))
    # Coordenadas dos clientes
    clientes_coordenadas = todas_coordenadas[1:]
    plt.scatter(clientes_coordenadas[:, 0], clientes_coordenadas[:, 1], c='blue', label='Clientes')
    plt.scatter(0, 0, c='red', label='Depósito')

    cores = plt.cm.get_cmap('tab20', len(rotas))

    for idx, rota in enumerate(rotas):
        if corrigir_sequencia:
            sequencia_rota = [0] + rota + [0]
            coordenadas_rota = todas_coordenadas[sequencia_rota]
        else:
            coordenadas_rota = todas_coordenadas[rota]
            
        plt.plot(coordenadas_rota[:, 0], coordenadas_rota[:, 1], color=cores(idx), label=f'Veículo {idx + 1}')

    plt.legend()
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title(titulo)
    
    return plt
