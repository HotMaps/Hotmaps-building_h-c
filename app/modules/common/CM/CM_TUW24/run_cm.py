import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW24.reproject_shp as reProj


def main(inShapefile, outShapefile, outEPSG=3035):
    reProj.change_projection(inShapefile, outShapefile, outEPSG)
