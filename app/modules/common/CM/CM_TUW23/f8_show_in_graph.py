import os
import sys
from osgeo import gdal
from osgeo import osr
import networkx as nx
import numpy as np
from scipy.ndimage import measurements
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from CM.CM_TUW0.rem_mk_dir import rm_mk_dir


def edge_representation(row_from_label, col_from_label, row_to_label,
                        col_to_label, distance_matrix, node_label_list,
                        edge_list, gt, outDir, epsg=3035):
    rm_mk_dir(outDir)
    G = nx.Graph()
    x0, y0 , w , h = gt[0], gt[3], gt[1], gt[5]
    X0 = x0 + w/2
    Y0 = y0 + h/2
    for k in range(edge_list.shape[0]):
        s, t, edge_weight = edge_list[k, :]
        s, t = int(s), int(t)
        py0_ind, px0_ind = row_from_label[s, t], col_from_label[s, t]
        py1_ind, px1_ind = row_to_label[s, t], col_to_label[s, t]
        px0, py0 = X0 + 100 * px0_ind, Y0 - 100 * py0_ind
        px1, py1 = X0 + 100 * px1_ind, Y0 - 100 * py1_ind
        # G.add_edge((px0, py0), (px1, py1), weight=distance_matrix[s, t])
        G.add_edge((px0, py0), (px1, py1), weight=edge_weight)
    nx.write_shp(G, outDir)
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(epsg)
    spatialRef.MorphToESRI()
    for item in ['nodes', 'edges']:
        prj_file = outDir + os.sep + item + '.prj'
        with open(prj_file, 'w') as file:
            file.write(spatialRef.ExportToWkt())


def edge_representation_old(label_raster, dh_bool_raster, distance_matrix, node_label_list,
                        edge_list, outDir, epsg=3035):
    rm_mk_dir(outDir)
    G = nx.Graph()
    label_ds = gdal.Open(label_raster)
    label_band = label_ds.GetRasterBand(1)
    label_arr = label_band.ReadAsArray()
    bool_ds = gdal.Open(dh_bool_raster)
    bool_band = bool_ds.GetRasterBand(1)
    bool_arr = bool_band.ReadAsArray()
    numLabels = np.max(label_arr)
    coords = measurements.center_of_mass(bool_arr, label_arr,
                                         index=np.arange(1, numLabels+1))
    gt = label_ds.GetGeoTransform()
    x0, y0 , w , h = gt[0], gt[3], gt[1], gt[5]
    bool_ds = label_ds = gt = None
    X0 = x0 + w/2
    Y0 = y0 + h/2
    x = []
    y = []
    for i, item in enumerate(coords):
        x.append(X0 + 100 * item[1])
        y.append(Y0 - 100 * item[0])
        if node_label_list[i]:
            G.add_node((x[i], y[i]))
    for k in range(edge_list.shape[0]):
        s, t, edge_weight = edge_list[k, :]
        s, t = int(s), int(t)
        # G.add_edge((x[s], y[s]), (x[t], y[t]), weight=distance_matrix[s, t])
        G.add_edge((x[s], y[s]), (x[t], y[t]), weight=edge_weight)
    nx.write_shp(G, outDir)
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(epsg)
    spatialRef.MorphToESRI()
    for item in ['nodes', 'edges']:
        prj_file = outDir + os.sep + item + '.prj'
        with open(prj_file, 'w') as file:
            file.write(spatialRef.ExportToWkt())

