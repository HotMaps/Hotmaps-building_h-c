import numpy as np
import pandas as pd
import geopandas as gpd
import time
from shapely.geometry import Point
from geopandas.tools import overlay
from geopandas import GeoDataFrame


    
def rasterize_no_shp(inShapefile):

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    rows = 10
    cols = 5
    x0 = 944000
    y0= 5415000
    x = x0 + np.sort((np.arange(rows)*np.ones(cols).reshape(cols,1)).reshape(1,rows*cols))*100
    y = y0 - (np.arange(cols)*np.ones(rows).reshape(rows,1)).reshape(1,rows*cols)*100
    d = {"X":x[0].tolist(),"Y":y[0].tolist()}
    df = pd.DataFrame(d)
    geometry = [Point(xy) for xy in zip(x[0].tolist(), y[0].tolist())]
    
    crs = {'init': 'epsg:3035'}
    geo_df = GeoDataFrame(df, crs=crs, geometry=geometry)
    
    geo_df1 = gpd.read_file(inShapefile)  
    outLyr_path = "/home/simulant/ag_lukas/personen/Mostafa/Wien Buildingblocks/testoverlay.shp"  
    overlaying(geo_df,geo_df1,1,outLyr_path)
    
if __name__ == "__main__":
    start = time.time()
    inShapefile = "/home/simulant/ag_lukas/personen/Mostafa/Wien Buildingblocks/NUTS3.shp"
    rasterize_no_shp(inShapefile)
    print(time.time() - start)