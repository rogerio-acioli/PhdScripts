import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

# Caminhos dos arquivos de entrada e saída
#input_file = 'C:/Users/roger/Downloads/enderecos.xlsx'
#output_file = 'C:/Users/roger/Downloads/enderecos_com_coordenadas.xlsx'

def create_clusters(file_path):
    # Leitura da planilha
    df = pd.read_excel(file_path)

    # Lista para armazenar resultados
    results = []

    # Loop através das cidades únicas
    for city in df['Cidade'].unique():
        city_df = df[df['Cidade'] == city].copy()

        # Lojas que faturam >= 200,000 se tornam clusters únicos
        high_revenue_stores = city_df[city_df['Faturamento'] >= 200000].copy()
        high_revenue_stores['Cluster'] = range(len(high_revenue_stores))

        # Lojas com faturamento < 200,000
        low_revenue_stores = city_df[city_df['Faturamento'] < 200000].copy()

        # Se não houver lojas de baixo faturamento, pula para a próxima cidade
        if low_revenue_stores.empty:
            results.append(high_revenue_stores)
            continue

        # Definição de clusters para lojas de baixo faturamento
        low_revenue_stores = low_revenue_stores.sort_values(by='Faturamento', ascending=False)
        low_revenue_stores['Cluster'] = -1  # Inicializando cluster como não definido

        # Algoritmo de clusterização
        current_cluster = max(high_revenue_stores['Cluster'].max(), 0) + 1
        current_sum = 0
        for idx, row in low_revenue_stores.iterrows():
            if current_sum + row['Faturamento'] > 200000:
                current_cluster += 1
                current_sum = 0
            low_revenue_stores.at[idx, 'Cluster'] = current_cluster
            current_sum += row['Faturamento']

        # Concatenando resultados
        results.append(pd.concat([high_revenue_stores, low_revenue_stores]))

    # Concatenando todas as cidades
    final_df = pd.concat(results)

    # Salvando em uma nova planilha de Excel
    final_df.to_excel('C:/Users/roger/Downloads/clusters_output.xlsx', index=False)


# Caminho para a planilha de entrada
file_path = 'C:/Users/roger/Downloads/lojas_faturamento.xlsx'
create_clusters(file_path)
