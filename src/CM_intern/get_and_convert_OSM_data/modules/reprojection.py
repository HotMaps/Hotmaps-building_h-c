# --------------------------------------- Header -------------------------------------------------
from qgis.core import *
import sip
import sys

linux = "linux" in sys.platform
if linux:
    sys.path.append("/usr/share/qgis/python/plugins")

API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
API_VERSION = 2
for name in API_NAMES:
    sip.setapi(name, API_VERSION)

from PyQt4.QtGui import *
#"""
app = QgsApplication([], True)

if linux:
    app.setPrefixPath("/usr/share/qgis/")
else:
    app.setPrefixPath("C:/OSGeo4W64/apps/qgis", True)
app.initQgis()


import processing
from processing.core.Processing import Processing
Processing.initialize()
Processing.updateAlgsList()
#"""
# ------------------------------------------------------------------------------------------------------------
# --------------------------------------- Additional imports -------------------------------------------------
from osgeo import gdal

def reprojection(input_lyr_path, output_lyr_path, buildings_input_feat):
	suffiex = input_lyr_path[-4:].lower()
	print(output_lyr_path)
	if suffiex == ".tif":
		input_lyr = QgsRasterLayer(input_lyr_path, buildings_input_feat)
		src_crs = input_lyr.crs().authid()
		extent = input_lyr.extent()
		xmin = extent.xMinimum()
		xmax = extent.xMaximum()
		ymin = extent.yMinimum()
		ymax = extent.yMaximum()
		processing.runalg("gdalogr:warpreproject",{ "INPUT" : input_lyr,
												"SOURCE_SRS" : src_crs,
												"DEST_SRS" : "EPSG:3035",
												"NO_DATA" : "",
												"TR" : 0.0,
												"METHOD" : 0,
												"RAST_EXT" : "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
												"EXT_CRS" : "EPSG:3035",
												"RTYPE" : 0,
												"COMPRESS" : 4,
												"JPEGCOMPRESSION" : 75,
												"ZLEVEL" : 6,
												"PREDICTOR" : 1,
												"TILED" : False,
												"BIGTIFF" : 2,
												"TFW" : False,
												"EXTRA" : "",
												"OUTPUT" : output_lyr_path })
	elif suffiex == ".shp":
		input_lyr = QgsVectorLayer(input_lyr_path, buildings_input_feat, "ogr")
		print("Start reprojection Layer: %s -> %s" % (input_lyr_path, output_lyr_path))
		processing.runalg('qgis:reprojectlayer', input_lyr, "EPSG:3035", output_lyr_path)
		
	else:
		sys.exit("The input file is not valid!")
	
	# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Close XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	#app.exitQgis()
	# if os.path.exists(temp_path):
	    # shutil.rmtree(temp_path)
	print("Reprojection done")
	return