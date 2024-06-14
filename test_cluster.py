from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np

# Coordenadas de latitude e longitude das lojas
coordinates = np.array([
    [40.712776, -74.005974],  # Loja 1
    [34.052235, -118.243683], # Loja 2
    [41.878113, -87.629799],  # Loja 3
    [29.760427, -95.369804],  # Loja 4
    [39.739236, -104.990251], # Loja 5
    [25.761680, -80.191790],  # Loja 6
    [51.507351, -0.127758],   # Loja 7
    [48.856613, 2.352222],    # Loja 8
    [35.689487, 139.691711],  # Loja 9
    [55.755825, 37.617298]    # Loja 10
])

# Número de clusters
n_clusters = 3

# Aplicar k-means
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
labels = kmeans.fit_predict(coordinates)

# Coordenadas dos centróides
centroids = kmeans.cluster_centers_

# Plotar os resultados
plt.scatter(coordinates[:, 0], coordinates[:, 1], c=labels, cmap='viridis', marker='o', s=100, label='Lojas')
plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='x', s=200, label='Centroides')
plt.xlabel('Latitude')
plt.ylabel('Longitude')
plt.title('Clusterização de Lojas usando K-Means')
plt.legend()
plt.grid(True)
plt.show()

print("Rótulos dos clusters:")
print(labels)