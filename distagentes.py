import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Caminho do arquivo
file_path = 'C:/Users/ra52440/OneDrive - AGCO Corp/00. ROGERIO ALVES_Documentos/Python/lojas.xlsx'

# Carregar dados do Excel
df = pd.read_excel(file_path)

# Calcular a magnitude (contagem de lojas por cidade)
df_magnitude = df['Cidade'].value_counts().reset_index()
df_magnitude.columns = ['Cidade', 'Magnitude']

# Remover duplicatas e manter apenas uma linha por cidade para coordenadas
df_coords = df.drop_duplicates(subset=['Cidade'])

# Combinar dados de magnitude com coordenadas das cidades
df_combined = pd.merge(df_magnitude, df_coords[['Cidade', 'Latitude', 'Longitude']], on='Cidade')

# Verificar os dados combinados
print(df_combined.head())

# Carregar o mapa do Brasil
mapa_brasil = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
mapa_brasil = mapa_brasil[mapa_brasil['name'] == 'Brazil']

# Criar um GeoDataFrame a partir dos dados combinados
gdf = gpd.GeoDataFrame(df_combined, geometry=gpd.points_from_xy(df_combined.Longitude, df_combined.Latitude))

# Plotar o mapa
fig, ax = plt.subplots(figsize=(15, 15))
mapa_brasil.plot(ax=ax, color='white', edgecolor='black')

# Plotar os pontos
# Aqui usamos a magnitude para determinar o tamanho dos pontos
gdf.plot(ax=ax, color='red', markersize=gdf['Magnitude']*10, alpha=0.5)

# Adicionar rótulos aos pontos
for x, y, label, magnitude in zip(gdf.geometry.x, gdf.geometry.y, gdf['Cidade'], gdf['Magnitude']):
    ax.text(x, y, f"{label} ({magnitude})", fontsize=8, ha='right', color='black')

# Configurar título e remover eixos
plt.title('Mapa de Lojas por Cidade no Brasil', fontsize=20)
plt.axis('off')

# Salvar o gráfico em alta resolução
plt.savefig('C:/Users/ra52440/OneDrive - AGCO Corp/00. ROGERIO ALVES_Documentos/Python/mapa_lojas_brasil.png', dpi=300)
plt.show()





