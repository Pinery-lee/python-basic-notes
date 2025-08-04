# 使用uv安装GDAL和PyTorch

1. 安装GDAL

   ```
   uv add pip
   pip install "https://github.com/cgohlke/geospatial-wheels/releases/download/v2025.1.20/GDAL-3.10.1-cp310-cp310-win_amd64.whl"
   ```

2. 安装PyTorch

   ```
   uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
   ```