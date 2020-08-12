import os
from landez import MBTilesBuilder, TilesManager

# From a TMS tile server
#tm = TilesManager(tiles_url="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
#                  tiles_headers={'User-Agent': 'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'})

tm = TilesManager(tiles_url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.jpg",
                  tiles_headers={'User-Agent': 'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'})

# trevassack
#tiles = tm.tileslist(bbox=(-5.225440815122283,50.0443122338314, 
#                           -5.171796634824432,50.06410175820282),
#                     zoomlevels=[14,15,16,17,18,19])

# falmouth
tiles = tm.tileslist(bbox=(-5.162955831669365,50.134767490127274,
                            -4.96932179846624, 50.197268922759214),
                     zoomlevels=[18,19])


def build_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

for tile in tiles:
    print(tile)
    path=str(tile[0])+"/"+str(tile[1])+"/"
    filename=str(tile[2])+".jpg"
    if not os.path.exists(path+filename):
        tilecontent = tm.tile(tile)  # download, extract or take from cache
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path+filename, 'wb') as f:
            f.write(tilecontent)
    else:
        print("skipped: "+path+filename)
    
