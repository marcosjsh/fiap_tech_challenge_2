from values import *
from helper import gerar_coordenadas_demandas_clientes, plotar_rotas
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from scipy.spatial.distance import cdist
import numpy as np


def criar_modelo_dados(clientes_coordenadas, clientes_demandas):
    dados = {}
    deposito_coordenadas = np.array([[0, 0]])  # Coordenadas do depósito
    todas_coordenadas = np.vstack([deposito_coordenadas, clientes_coordenadas])
    
    # Matriz de distâncias
    matriz_distancias = cdist(todas_coordenadas, todas_coordenadas)
    dados['matriz_distancias'] = (matriz_distancias * 1000).astype(int).tolist()
    
    # Demandas
    dados['demandas'] = [0] + clientes_demandas.tolist()  # Demanda do depósito é 0
    dados['capacidades_veiculos'] = [capacidade_veiculo] * numero_veiculos
    dados['numero_veiculos'] = numero_veiculos
    dados['deposito'] = 0
    return dados


def imprimir_solucao(dados, gerenciador, roteamento, solucao, todas_coordenadas):
    total_distancia = 0
    total_carga = 0
    todas_rotas = []  # Lista para armazenar as rotas de todos os veículos
    for veiculo_id in range(dados['numero_veiculos']):
        indice = roteamento.Start(veiculo_id)
        plano_rota = f'Veículo {veiculo_id + 1}:\n'
        rota_distancia = 0
        rota_carga = 0
        rota = []
        while not roteamento.IsEnd(indice):
            no_indice = gerenciador.IndexToNode(indice)
            rota_carga += dados['demandas'][no_indice]
            rota.append(no_indice)
            indice_anterior = indice
            indice = solucao.Value(roteamento.NextVar(indice))
            rota_distancia += roteamento.GetArcCostForVehicle(indice_anterior, indice, veiculo_id)
        rota.append(gerenciador.IndexToNode(indice))
        plano_rota += f" Rota: {rota}\n"
        plano_rota += f" Carga da rota: {rota_carga}\n"
        plano_rota += f" Distância da rota: {rota_distancia / 1000:.2f} unidades\n"
        print(plano_rota)
        total_distancia += rota_distancia
        total_carga += rota_carga
        todas_rotas.append(rota)  # Armazenar a rota do veículo
    print(f"Distância total de todas as rotas: {total_distancia / 1000:.2f} unidades")
    print(f"Carga total transportada: {total_carga}")
    
    # Chamar a função para visualizar as rotas
    plotar_rotas('Rotas Geradas pelo OR-Tools', todas_rotas, todas_coordenadas).show()
    

def resolver_vrp():
    # Gerar ou carregar os dados dos clientes
    clientes_coordenadas, clientes_demandas = gerar_coordenadas_demandas_clientes()
    
    # Criar o modelo de dados
    dados = criar_modelo_dados(clientes_coordenadas, clientes_demandas)
    
    # Criar o gerenciador de índices
    gerenciador = pywrapcp.RoutingIndexManager(len(dados['matriz_distancias']), dados['numero_veiculos'], dados['deposito'])
    
    # Criar o modelo de roteamento
    roteamento = pywrapcp.RoutingModel(gerenciador)
    
    # Função de custo (distância)
    def distancia_callback(de_origem_idx, para_destino_idx):
        de_origem_no = gerenciador.IndexToNode(de_origem_idx)
        para_destino_no = gerenciador.IndexToNode(para_destino_idx)
        return dados['matriz_distancias'][de_origem_no][para_destino_no]
    
    indice_callback_transito = roteamento.RegisterTransitCallback(distancia_callback)
    roteamento.SetArcCostEvaluatorOfAllVehicles(indice_callback_transito)
    
    # Restrições de capacidade
    def demanda_callback(de_idx):
        from_node = gerenciador.IndexToNode(de_idx)
        return dados['demandas'][from_node]
    
    indice_callback_demanda = roteamento.RegisterUnaryTransitCallback(demanda_callback)
    roteamento.AddDimensionWithVehicleCapacity(
        indice_callback_demanda,
        0,  # Sem capacidade excedente
        dados['capacidades_veiculos'],
        True,
        'Capacidade'
    )
    
    # Parâmetros de busca
    parametros_busca = pywrapcp.DefaultRoutingSearchParameters()
    parametros_busca.time_limit.seconds = 30  # Tempo máximo de busca
    parametros_busca.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    
    # Resolver o problema
    solucao = roteamento.SolveWithParameters(parametros_busca)
    
    if solucao:
        # Coordenadas completas (depósito + clientes)
        deposito_coordenadas = np.array([[0, 0]])  # Coordenadas do depósito
        todas_coordenadas = np.vstack([deposito_coordenadas, clientes_coordenadas])
        imprimir_solucao(dados, gerenciador, roteamento, solucao, todas_coordenadas)
    else:
        print('Nenhuma solução encontrada!')
        

if __name__ == '__main__':
    resolver_vrp()