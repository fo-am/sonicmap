import os
from landez import MBTilesBuilder, TilesManager

# From a TMS tile server
tm = TilesManager(tiles_url="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                  tiles_headers={'User-Agent': 'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'})

tiles = tm.tileslist(bbox=(-5.225440815122283,50.0443122338314, 
                           -5.171796634824432,50.06410175820282),
                     zoomlevels=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19])

def build_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

for tile in tiles:
    print(tile)
    tilecontent = tm.tile(tile)  # download, extract or take from cache
    path=str(tile[0])+"/"+str(tile[1])+"/"              
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path+str(tile[2])+".png", 'wb') as f:
        f.write(tilecontent)
