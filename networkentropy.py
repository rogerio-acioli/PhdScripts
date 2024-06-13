import pandas as pd
import numpy as np
from math import log2


def calculate_entropy(probabilities):
    return -sum(p * log2(p) for p in probabilities if p > 0)


def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df


def calculate_entropies(df):
    levels = df['Nível'].unique()

    # Entropia Vertical (Distribuição dos níveis)
    level_counts = df['Nível'].value_counts(normalize=True)
    vertical_entropy = calculate_entropy(level_counts)

    # Entropia Horizontal (Distribuição das unidades dentro de cada nível)
    horizontal_entropies = []
    for level in levels:
        units_in_level = df[df['Nível'] == level]
        unit_counts = units_in_level['Unidade'].value_counts(normalize=True)
        horizontal_entropy = calculate_entropy(unit_counts)
        horizontal_entropies.append(horizontal_entropy)

    # Média da Entropia Horizontal
    average_horizontal_entropy = np.mean(horizontal_entropies)

    # Entropia Total
    total_entropy = vertical_entropy + average_horizontal_entropy

    return vertical_entropy, average_horizontal_entropy, total_entropy


def write_to_excel(file_path, vertical_entropy, horizontal_entropy, total_entropy):
    output_df = pd.DataFrame({
        'Entropia Vertical': [vertical_entropy],
        'Entropia Horizontal': [horizontal_entropy],
        'Entropia Total': [total_entropy]
    })
    output_df.to_excel(file_path, index=False)


def main(input_file, output_file):
    df = read_excel(input_file)
    vertical_entropy, horizontal_entropy, total_entropy = calculate_entropies(df)
    write_to_excel(output_file, vertical_entropy, horizontal_entropy, total_entropy)

if __name__ == "__main__":
    input_file = 'C:/Users/ra52440/Downloads/Exame Final P2/estrutura_organizacional.xlsx'  # Substitua pelo nome do seu arquivo de entrada
    output_file = 'C:/Users/ra52440/Downloads/Exame Final P2/entropia_organizacional.xlsx'  # Nome do arquivo de saída
    main(input_file, output_file)