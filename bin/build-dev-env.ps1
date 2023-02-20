conda create -n cnwi-gee-dev -c conda-forge python=3.10 geopandas pandas earthengine-api matplotlib python-dotenv geemap -y
conda activate cnwi-gee-dev

conda remove pyproj --force -y
python -m pip install pyproj

Write-Output "Installing CNWI package"
python -m pip install -e  "../"
