from values import *
from helper import gerar_coordenadas_demandas_clientes, plotar_rotas
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import numpy as np
import random


def distancia_genetica(ind1, ind2):
    # Defina uma função para calcular a distância genética entre dois indivíduos
    return sum(g1 != g2 for g1, g2 in zip(ind1, ind2)) / len(ind1)


def calcular_diversidade(populacao):
    matriz_distancias = []
    for ind1 in populacao:
        distancias = [distancia_genetica(ind1, ind2) for ind2 in populacao]
        matriz_distancias.append(np.mean(distancias))
    return np.mean(matriz_distancias)


def ajustar_taxa_mutacao(diversidade_populacao, taxa_mutacao_base, limite_diversidade):
    if diversidade_populacao < limite_diversidade:
        return min(taxa_mutacao_base * 2, 0.1)  # Limite máximo de 10%
    else:
        return taxa_mutacao_base


def calcular_fitness(individuo, matriz_distancias, clientes_demandas, capacidade_veiculo):
    total_distancia = 0
    total_penalidade = 0
    carga_veiculo = 0
    rota = [0]  # Inicia no depósito

    for gene in individuo[1:]:
        if gene == 0:
            # Fim da rota atual
            total_distancia += matriz_distancias[rota[-1]][0]  # Retorna ao depósito
            if carga_veiculo > capacidade_veiculo:
                total_penalidade += (carga_veiculo - capacidade_veiculo) * 1000  # Penalização pesada
            # Reinicia para o próximo veículo
            carga_veiculo = 0
            rota = [0]
        else:
            total_distancia += matriz_distancias[rota[-1]][gene]
            carga_veiculo += clientes_demandas[gene - 1]
            rota.append(gene)

    # Verificar a última rota
    if rota[-1] != 0:
        total_distancia += matriz_distancias[rota[-1]][0]
        if carga_veiculo > capacidade_veiculo:
            total_penalidade += (carga_veiculo - capacidade_veiculo) * 1000

    fitness = total_distancia + total_penalidade
    return fitness


def selecao(populacao, fitnesses):
    idx1, idx2 = random.sample(range(len(populacao)), 2)
    if fitnesses[idx1] < fitnesses[idx2]:
        return populacao[idx1]
    else:
        return populacao[idx2]
    
    
def crossover_avancado(pai1, pai2, clientes_demandas, capacidade_veiculo, taxa_crossover=0.8):
    # Decidir se o crossover será aplicado com base na taxa de crossover
    if random.random() < taxa_crossover:
        # Aplicar o crossover avançado
        def extrair_rotas(individuo):
            rotas = []
            rota = []
            for gene in individuo[1:]:
                if gene == 0:
                    if rota:
                        rotas.append(rota)
                    rota = []
                else:
                    rota.append(gene)
            return rotas

        rotas_pai1 = extrair_rotas(pai1)
        rotas_pai2 = extrair_rotas(pai2)
        
        # Selecionar rotas para herdar
        num_rotas = min(len(rotas_pai1), len(rotas_pai2))
        num_herdar = random.randint(1, num_rotas)
        
        rotas_herdadas = []
        clientes_herdados = set()
        
        # Herança de rotas do primeiro pai
        random.shuffle(rotas_pai1)
        for rota in rotas_pai1:
            if len(rotas_herdadas) >= num_herdar:
                break
            rotas_herdadas.append(rota)
            clientes_herdados.update(rota)
        
        # Preencher com rotas do segundo pai
        clientes_restantes = [gene for gene in range(1, numero_clientes + 1) if gene not in clientes_herdados]
        random.shuffle(clientes_restantes)
        
        # Construir rotas adicionais para atender os clientes restantes
        novas_rotas = []
        rota_atual = []
        carga_atual = 0
        
        for cliente in clientes_restantes:
            demanda = clientes_demandas[cliente - 1]
            if carga_atual + demanda <= capacidade_veiculo:
                rota_atual.append(cliente)
                carga_atual += demanda
            else:
                novas_rotas.append(rota_atual)
                rota_atual = [cliente]
                carga_atual = demanda
        if rota_atual:
            novas_rotas.append(rota_atual)
        
        # Combinar rotas herdadas e novas rotas
        rotas_filho = rotas_herdadas + novas_rotas
        random.shuffle(rotas_filho)
        
        # Construir indivíduo filho
        filho = [0]
        for rota in rotas_filho:
            filho.extend(rota)
            filho.append(0)
        
        return filho
    else:
        # Não aplicar crossover, retornar um dos pais
        # Pode-se escolher o melhor pai ou um aleatório
        # Aqui, retornaremos um dos pais aleatoriamente
        return random.choice([pai1.copy(), pai2.copy()])


def mutacao_inversao(individuo, taxa_mutacao=0.02):
    mutado = individuo.copy()
    if random.random() < taxa_mutacao:
        # Encontrar posições não zero
        idx = [i for i, gene in enumerate(mutado) if gene != 0]
        if len(idx) >= 2:
            i1, i2 = sorted(random.sample(idx, 2))
            # Inverter a subsequência
            mutado[i1:i2+1] = mutado[i1:i2+1][::-1]
    return mutado


def criar_populacao_inicial(tamanho_populacao, numero_clientes, numero_veiculos):
    populacao = []
    clientes = list(range(1, numero_clientes + 1))
    for _ in range(tamanho_populacao):
        random.shuffle(clientes)
        num_zeros = numero_veiculos - 1  # Número de separadores
        posicoes = sorted(random.sample(range(1, numero_clientes), num_zeros))
        individuo = [0]
        ultimo_pos = 0
        for pos in posicoes:
            individuo.extend(clientes[ultimo_pos:pos])
            individuo.append(0)
            ultimo_pos = pos
        individuo.extend(clientes[ultimo_pos:])
        individuo.append(0)
        populacao.append(individuo)
    return populacao


# def executar_algoritmo_genetico():
#     # Gerar ou carregar os dados dos clientes
#     clientes_coordenadas, clientes_demandas = gerar_coordenadas_demandas_clientes()
    
#     # Coordenadas completas (depósito + clientes)
#     deposito_coordenadas = np.array([[0, 0]])  # Coordenadas do depósito
#     todas_coordenadas = np.vstack([deposito_coordenadas, clientes_coordenadas])
    
#     # Matriz de distâncias
#     matriz_distancias = cdist(todas_coordenadas, todas_coordenadas)
    
#     # Parâmetros do AG
#     tamanho_populacao = TAMANHO_POPULACAO
#     numero_geracoes = NUMERO_GERACOES
#     taxa_mutacao = TAXA_MUTACAO_BASE
#     tamanho_elite = TAXA_ELITISMO
    
#     # Criar população inicial
#     populacao = criar_populacao_inicial(tamanho_populacao, numero_clientes, numero_veiculos)
    
#     melhor_individuo = None
#     melhor_fitness = float('inf')
#     historico_fitness = []
    
#     for geracao in range(numero_geracoes):
#         # Calcular fitnesses
#         fitnesses = []
#         for individuo in populacao:
#             fitness = calcular_fitness(individuo, matriz_distancias, clientes_demandas, capacidade_veiculo)
#             fitnesses.append(fitness)
#             if fitness < melhor_fitness:
#                 melhor_fitness = fitness
#                 melhor_individuo = individuo
    
#         historico_fitness.append(melhor_fitness)
    
#         # Elitismo
#         populacao_ordenada = [x for _, x in sorted(zip(fitnesses, populacao), key=lambda pair: pair[0])]
#         elite_individuos = populacao_ordenada[:tamanho_elite]
    
#         # Gerar nova população
#         nova_populacao = elite_individuos.copy()  # Preservar elite
#         num_descendentes = tamanho_populacao - tamanho_elite
    
#         for _ in range(num_descendentes):
#             pai1 = selecao(populacao, fitnesses)
#             pai2 = selecao(populacao, fitnesses)
#             filho = crossover_avancado(pai1, pai2, clientes_demandas, capacidade_veiculo, TAXA_CROSSOVER)
#             filho = mutacao_inversao(filho, taxa_mutacao)
#             nova_populacao.append(filho)
    
#         populacao = nova_populacao
    
#         if (geracao + 1) % 50 == 0 or geracao == 0:
#             print(f"Geração {geracao + 1}: Melhor Fitness = {melhor_fitness:.2f}")
    
#     return melhor_individuo, melhor_fitness, historico_fitness, clientes_coordenadas, clientes_demandas, matriz_distancias
def executar_algoritmo_genetico():
    # Gerar ou carregar os dados dos clientes
    clientes_coordenadas, clientes_demandas = gerar_coordenadas_demandas_clientes()
    
    # Coordenadas completas (depósito + clientes)
    deposito_coordenadas = np.array([[0, 0]])  # Coordenadas do depósito
    todas_coordenadas = np.vstack([deposito_coordenadas, clientes_coordenadas])
    
    # Matriz de distâncias
    matriz_distancias = cdist(todas_coordenadas, todas_coordenadas)
    
    # Parâmetros do AG
    tamanho_populacao = TAMANHO_POPULACAO
    numero_geracoes = NUMERO_GERACOES
    taxa_mutacao_base = TAXA_MUTACAO_BASE
    tamanho_elite = TAXA_ELITISMO
    
    # Criar população inicial
    populacao = criar_populacao_inicial(tamanho_populacao, numero_clientes, numero_veiculos)
    
    melhor_individuo = None
    melhor_fitness = float('inf')
    historico_fitness = []
    
    for geracao in range(numero_geracoes):
        # Calcular a diversidade da população
        diversidade = calcular_diversidade(populacao)
        # Ajustar a taxa de mutação com base na diversidade
        taxa_mutacao = ajustar_taxa_mutacao(diversidade, taxa_mutacao_base, LIMITE_DIVERSIDADE)
        
        # Calcular fitnesses
        fitnesses = []
        for individuo in populacao:
            fitness = calcular_fitness(individuo, matriz_distancias, clientes_demandas, capacidade_veiculo)
            fitnesses.append(fitness)
            if fitness < melhor_fitness:
                melhor_fitness = fitness
                melhor_individuo = individuo
    
        historico_fitness.append(melhor_fitness)
    
        # Elitismo
        populacao_ordenada = [x for _, x in sorted(zip(fitnesses, populacao), key=lambda pair: pair[0])]
        elite_individuos = populacao_ordenada[:tamanho_elite]
    
        # Gerar nova população
        nova_populacao = elite_individuos.copy()  # Preservar elite
        num_descendentes = tamanho_populacao - tamanho_elite
    
        for _ in range(num_descendentes):
            pai1 = selecao(populacao, fitnesses)
            pai2 = selecao(populacao, fitnesses)
            filho = crossover_avancado(pai1, pai2, clientes_demandas, capacidade_veiculo, TAXA_CROSSOVER)
            filho = mutacao_inversao(filho, taxa_mutacao)
            nova_populacao.append(filho)
    
        populacao = nova_populacao
    
        if (geracao + 1) % 50 == 0 or geracao == 0:
            print(f"Geração {geracao + 1}: Melhor Fitness = {melhor_fitness:.2f}, Diversidade = {diversidade:.4f}, Taxa de Mutação = {taxa_mutacao:.4f}")
    
    return melhor_individuo, melhor_fitness, historico_fitness, clientes_coordenadas, clientes_demandas, matriz_distancias


def exibir_resultados(melhor_individuo, melhor_fitness, historico_fitness, clientes_coordenadas, clientes_demandas, matriz_distancias):
    # Exibir o melhor indivíduo encontrado
    print("\nMelhor solução encontrada:")
    print(f"Fitness: {melhor_fitness:.2f}")
    
    # Extrair as rotas
    rotas = []
    rota = []
    for gene in melhor_individuo[1:]:
        if gene == 0:
            if rota:
                rotas.append(rota)
            rota = []
        else:
            rota.append(gene)
    
    # Coordenadas completas para plotagem
    deposito_coordenadas = np.array([[0, 0]])
    todas_coordenadas = np.vstack([deposito_coordenadas, clientes_coordenadas])
    
    # Exibir detalhes das rotas
    total_distancia = 0
    total_carga = 0
    for idx, rota in enumerate(rotas):
        sequencia_rota = [0] + rota + [0]
        distancia_rota = sum(matriz_distancias[sequencia_rota[i]][sequencia_rota[i+1]] for i in range(len(sequencia_rota)-1))
        carga_rota = sum(clientes_demandas[np.array(rota) - 1])
        total_distancia += distancia_rota
        total_carga += carga_rota
        print(f"Veículo {idx + 1}: Rota {sequencia_rota} | Carga: {carga_rota} | Distância: {distancia_rota:.2f} unidades")
    
    print(f"\nDistância total percorrida: {total_distancia:.2f} unidades")
    print(f"\nCarga total transportada: {total_carga}")
    
    # Plotar a evolução do fitness
    plt.figure(figsize=(10, 6))
    plt.plot(historico_fitness)
    plt.xlabel('Geração')
    plt.ylabel('Melhor Fitness')
    plt.title('Evolução do Melhor Fitness com Operadores Avançados')
    plt.grid(True)
    plt.show()
    
    # Visualizar as rotas
    plotar_rotas('Rotas Geradas pelo Algoritmo Genético com Operadores Avançados', rotas, todas_coordenadas, True).show()
    

if __name__ == '__main__':
    melhor_individuo, melhor_fitness, historico_fitness, clientes_coordenadas, clientes_demandas, matriz_distancias = executar_algoritmo_genetico()
    exibir_resultados(melhor_individuo, melhor_fitness, historico_fitness, clientes_coordenadas, clientes_demandas, matriz_distancias)