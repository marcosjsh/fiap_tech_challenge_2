numero_clientes = 20
numero_veiculos = 3
capacidade_veiculo = 100
lote_minimo = 5
lote_maximo = 20
random_seed = 42

TAMANHO_POPULACAO = 200
NUMERO_GERACOES = 2500
TAXA_MUTACAO_BASE = 0.05
TAXA_CROSSOVER = 0.7
TAXA_ELITISMO = int(0.05 * TAMANHO_POPULACAO) # X% da população
LIMITE_DIVERSIDADE = 0.775

COORDENADAS_CLIENTES_FILE = "coordenadas_clientes.csv"
DEMANDAS_CLIENTES_FILE = "demandas_clientes.csv"

MATRIZ_DISTANCIAS_STR = 'matriz_distancias'
DEMANDAS_STR = 'demandas'
CAPACIDADE_VEICULO_STR = 'capacidade_veiculo'
NUMERO_VEICULOS_STR = 'numero_veiculos'
DEPOSITO_STR = 'deposito'
