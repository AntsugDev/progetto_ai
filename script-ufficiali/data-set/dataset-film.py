import kagglehub
from kagglehub import KaggleDatasetAdapter

path = kagglehub.dataset_download("kanchana1990/hollywood-2025-media-hype-and-sentiment")

print("Path to dataset files:", path)