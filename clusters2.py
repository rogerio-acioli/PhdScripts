import pandas as pd


def clean_data(df):
    # Remove espaços em branco e caracteres invisíveis das strings
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def create_clusters(file_path):
    # Leitura da planilha
    df = pd.read_excel(file_path)

    # Limpeza dos dados
    df = clean_data(df)

    # Verificação de valores nulos
    if df.isnull().values.any():
        null_columns = df.columns[df.isnull().any()].tolist()
        null_rows = df[df.isnull().any(axis=1)].index.tolist()
        raise ValueError(f"A planilha contém valores nulos nas colunas: {null_columns} nas linhas: {null_rows}")

    # Verificação da existência da coluna 'ID'
    if 'ID' not in df.columns:
        raise KeyError("A coluna 'ID' não foi encontrada na planilha.")

    # Lista para armazenar resultados
    results = []

    # Contador global de clusters
    global_cluster_counter = 0

    # Loop através das cidades únicas
    for city in df['Cidade'].unique():
        city_df = df[df['Cidade'] == city].copy()
        print(f"Processando a cidade: {city}")

        if city_df.empty:
            print(f"Nenhuma loja encontrada na cidade: {city}")
            continue

        # Lojas que faturam >= 200,000 se tornam clusters únicos
        high_revenue_stores = city_df[city_df['Faturamento'] >= 200000].copy()
        high_revenue_stores['Cluster'] = range(global_cluster_counter,
                                               global_cluster_counter + len(high_revenue_stores))
        global_cluster_counter += len(high_revenue_stores)

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
        current_sum = 0
        current_cluster = global_cluster_counter
        for idx, row in low_revenue_stores.iterrows():
            if current_sum + row['Faturamento'] > 200000:
                print(f"Novo cluster iniciado na cidade {city}: Cluster {current_cluster} com somatória {current_sum}")
                current_cluster += 1
                current_sum = 0
            low_revenue_stores.at[idx, 'Cluster'] = current_cluster
            current_sum += row['Faturamento']
            print(f"Loja ID {row['ID']} adicionada ao Cluster {current_cluster} com somatória {current_sum}")

        global_cluster_counter = current_cluster + 1

        # Concatenando resultados
        results.append(pd.concat([high_revenue_stores, low_revenue_stores]))

    # Concatenando todas as cidades
    final_df = pd.concat(results)

    # Salvando em uma nova planilha de Excel
    final_df.to_excel('C:/Users/roger/Downloads/clusters_output.xlsx', index=False)


# Caminho para a planilha de entrada
file_path = 'C:/Users/roger/Downloads/lojas_faturamento.xlsx'

# Chamando a função para criar clusters
create_clusters(file_path)