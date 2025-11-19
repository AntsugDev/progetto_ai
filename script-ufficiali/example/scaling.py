from sklearn.preprocessing import StandardScaler, MinMaxScaler
import numpy as np

# Dati esempio
dati = np.array([[1500, 10], [3000, 20], [4500, 30]])

# StandardScaler
scaler_std = StandardScaler()
dati_std = scaler_std.fit_transform(dati)
print("StandardScaler:")
print(dati_std)
# Output: [[-1.22 -1.22], [0     0    ], [1.22  1.22 ]]

# MinMaxScaler  
scaler_minmax = MinMaxScaler()
dati_minmax = scaler_minmax.fit_transform(dati)
print("MinMaxScaler:")
print(dati_minmax)
# Output: [[0   0], [0.5 0.5], [1   1  ]]