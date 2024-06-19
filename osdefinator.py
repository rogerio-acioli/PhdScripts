import pandas as pd
import numpy as np
from math import log2

def calculate_entropy(probabilities):
    return -sum(p * log2(p) for p in probabilities if p > 0)

def read_excel(file_path):
    return pd.read_excel(file_path)

def calculate_entropies(df):
    entropy_results = []

    for index, row in df.iterrows():
        try:
            levels = int(row['Níveis'])
            members_per_level = []
            for i in range(1, levels + 1):
                column_name = f'Membros_Nivel_{i}'
                if not pd.isna(row[column_name]):
                    members_per_level.append(int(row[column_name]))

            total_members = sum(members_per_level)
            if total_members == 0:
                continue  # Skip this row if there are no members

            # Entropia Vertical (Distribuição dos níveis)
            level_distribution = [members / total_members for members in members_per_level]
            vertical_entropy = calculate_entropy(level_distribution)

            # Entropia Horizontal (Distribuição dos membros dentro de cada nível)
            horizontal_entropies = []
            for members in members_per_level:
                if members > 0:
                    member_probability = 1 / members
                    horizontal_entropy = calculate_entropy([member_probability] * members)
                    horizontal_entropies.append(horizontal_entropy)

            average_horizontal_entropy = np.mean(horizontal_entropies) if horizontal_entropies else 0

            # Entropia Total
            total_entropy = vertical_entropy + average_horizontal_entropy

            entropy_results.append({
                'Estrutura': row['Estrutura'],
                'Entropia Vertical': vertical_entropy,
                'Entropia Horizontal': average_horizontal_entropy,
                'Entropia Total': total_entropy,
                'Total_Membros': total_members  # Adicionando a coluna Total_Membros
            })
        except Exception as e:
            print(f"Error processing row {index}: {e}")

    return pd.DataFrame(entropy_results)

def calcular_valor_estrutura(membros_por_nivel, n_departamentos, intensidade_interacao, compartilhamento_lateral):
    n_niveis = len(membros_por_nivel)
    n_total_membros = sum(membros_por_nivel.values())

    # Fórmula do valor conforme o modelo
    valor = intensidade_interacao ** 2 * n_departamentos * (
            (1 + (n_departamentos - 2) * intensidade_interacao + (n_departamentos - 1) * (
                        compartilhamento_lateral ** 2 - 2 * compartilhamento_lateral * intensidade_interacao))
            / (1 - intensidade_interacao)
    )
    return valor

def processar_planilha(entrada, saida):
    df = read_excel(entrada)

    # Calcular entropias
    entropia_df = calculate_entropies(df)

    resultados = []

    for index, row in df.iterrows():
        try:
            membros_por_nivel = {}
            for col in df.columns:
                if 'Membros_Nivel' in col:
                    if not pd.isna(row[col]):
                        nivel = int(col.split('_')[-1])
                        membros_por_nivel[nivel] = int(row[col])

            n_departamentos = int(row['Numero_de_Departamentos'])

            # Valores arbitrários para intensidade_interacao e compartilhamento_lateral
            intensidade_interacao = 0.5
            compartilhamento_lateral = 0.3

            # Calcular valor da estrutura
            valor = calcular_valor_estrutura(membros_por_nivel, n_departamentos, intensidade_interacao, compartilhamento_lateral)

            resultado = {col: row[col] for col in df.columns}
            resultado['Valor_da_Estrutura'] = valor

            resultados.append(resultado)
        except Exception as e:
            print(f"Error processing row {index}: {e}")

    valor_df = pd.DataFrame(resultados)

    # Combinar os resultados das entropias e do valor da estrutura
    final_df = pd.merge(entropia_df, valor_df, on='Estrutura')

    final_df.to_excel(saida, index=False)

if __name__ == "__main__":
    arquivo_entrada = 'C:/Users/roger/OneDrive/Doutorado/Python/estrutura_organizacional.xlsx'  # Substitua pelo nome do seu arquivo de entrada
    arquivo_saida = 'C:/Users/roger/OneDrive/Doutorado/Python/resultado_organizacional.xlsx'  # Nome do arquivo de saída
    processar_planilha(arquivo_entrada, arquivo_saida)
