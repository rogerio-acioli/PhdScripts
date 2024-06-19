import pandas as pd
import numpy as np
from math import log2


def calculate_entropy(probabilities):
    return -sum(p * log2(p) for p in probabilities if p > 0)


def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df


def calculate_entropies(df):
    results = []

    for index, row in df.iterrows():
        levels = row['Níveis']
        members_per_level = [row[f'Membros_Nivel_{i}'] for i in range(1, levels + 1) if
                             not pd.isna(row[f'Membros_Nivel_{i}'])]

        total_members = sum(members_per_level)

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

        results.append({
            'Estrutura': row['Estrutura'],
            'Entropia Vertical': vertical_entropy,
            'Entropia Horizontal': average_horizontal_entropy,
            'Entropia Total': total_entropy
        })

    return pd.DataFrame(results)


def write_to_excel(file_path, result_df):
    result_df.to_excel(file_path, index=False)


def main(input_file, output_file):
    df = read_excel(input_file)
    result_df = calculate_entropies(df)
    write_to_excel(output_file, result_df)

if __name__ == "__main__":
    input_file = 'C:/Users/roger/OneDrive/Doutorado/Python/estrutura_organizacional.xlsx'  # Substitua pelo nome do seu arquivo de entrada
    output_file = 'C:/Users/roger/OneDrive/Doutorado/Python/entropia_organizacional.xlsx'  # Nome do arquivo de saída
    main(input_file, output_file)