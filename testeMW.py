import pandas as pd
from scipy.stats import mannwhitneyu


# Função para realizar o Teste de Mann-Whitney e salvar os resultados
def mann_whitney_test_and_save(input_file, output_file):
    # Ler o arquivo Excel de entrada
    df = pd.read_excel(input_file)

    # Verificar se o dataframe contém a coluna 'Grupo' e as colunas de perguntas
    if 'Grupo' not in df.columns:
        raise ValueError("A coluna 'Grupo' não está presente no arquivo Excel.")

    # Verificar se há 19 colunas de perguntas
    question_columns = [f'P{i}' for i in range(1, 20)]
    for col in question_columns:
        if col not in df.columns:
            raise ValueError(f"A coluna '{col}' não está presente no arquivo Excel.")

    # Separar os dados em dois grupos
    grupo1 = df[df['Grupo'] == 'G1']
    grupo2 = df[df['Grupo'] == 'G2']

    results = []

    # Realizar o Teste de Mann-Whitney para cada pergunta
    for col in question_columns:
        stat, p_value = mannwhitneyu(grupo1[col], grupo2[col])
        results.append({'Pergunta': col, 'Estatística U': stat, 'Valor-p': p_value})

    # Criar um dataframe com os resultados
    results_df = pd.DataFrame(results)

    # Salvar os resultados em um arquivo Excel
    results_df.to_excel(output_file, index=False)

    print(f"Resultados salvos em '{output_file}'.")


# Caminhos para o arquivo de entrada e saída
input_file_path = 'C:/Users/ra52440/OneDrive - AGCO Corp/00. ROGERIO ALVES_Documentos/Python/dadosMW.xlsx'
output_file_path = 'C:/Users/ra52440/OneDrive - AGCO Corp/00. ROGERIO ALVES_Documentos/Python/results_MW.xlsx'

# Executar a função para realizar o teste e salvar os resultados
mann_whitney_test_and_save(input_file_path, output_file_path)

# Caminho para o arquivo Excel
file_path = 'C:/Users/ra52440/OneDrive - AGCO Corp/00. ROGERIO ALVES_Documentos/Python/dadosMW.xlsx'
