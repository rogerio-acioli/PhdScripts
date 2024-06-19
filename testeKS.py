import pandas as pd
from scipy.stats import ks_2samp


def ks_test_excel(input_file, sheet_name='Sheet1'):
    # Lendo o arquivo Excel
    df = pd.read_excel(input_file, sheet_name=sheet_name)

    # Verificando se o arquivo possui as colunas esperadas
    expected_columns = ['Pergunta', 'Grupo', 'Resposta']
    if not all(col in df.columns for col in expected_columns):
        raise ValueError(f"O arquivo Excel deve conter as colunas: {expected_columns}")

    # Filtrando os dados para os dois grupos
    g1 = df[df['Grupo'] == 'G1']
    g2 = df[df['Grupo'] == 'G2']

    # Preparando o resultado
    ks_results = {'Pergunta': [], 'Statistic': [], 'P-value': []}

    # Realizando o teste KS para cada pergunta
    perguntas = df['Pergunta'].unique()
    for pergunta in perguntas:
        g1_respostas = g1[g1['Pergunta'] == pergunta]['Resposta']
        g2_respostas = g2[g2['Pergunta'] == pergunta]['Resposta']

        # Realizando o teste KS
        statistic, p_value = ks_2samp(g1_respostas, g2_respostas)

        # Salvando os resultados
        ks_results['Pergunta'].append(pergunta)
        ks_results['Statistic'].append(statistic)
        ks_results['P-value'].append(p_value)

    # Convertendo os resultados para um DataFrame
    results_df = pd.DataFrame(ks_results)

    # Salvando os resultados em um novo arquivo Excel
    output_file = 'C:/Users/ra52440/OneDrive - AGCO Corp/00. ROGERIO ALVES_Documentos/Python/ks_test_results.xlsx'
    results_df.to_excel(output_file, index=False)
    print(f"Resultados do Teste KS salvos em: {output_file}")


# Exemplo de uso
ks_test_excel('C:/Users/ra52440/OneDrive - AGCO Corp/00. ROGERIO ALVES_Documentos/Python/dados.xlsx')
