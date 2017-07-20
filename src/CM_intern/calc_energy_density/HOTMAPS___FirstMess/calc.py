from qgis.core import *
import processing

from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

for i in range(15):
    for j in range(15):
        Lyr1_path = "/home/simulant/ag_lukas/personen/Mostafa/GasGrid/10km/10km_" + str('%04d' % (i)) + "_" + str('%04d' % (j)) + ".tif"
        Lyr2_path = "/home/simulant/ag_lukas/personen/Mostafa/GasGrid/0km/0km_" + str('%04d' % (i)) + "_" + str('%04d' % (j)) + ".tif"
        res = "/home/simulant/ag_lukas/personen/Mostafa/GasGrid/Result/10_0km/10_0km_" + str('%04d' % (i)) + "_" + str('%04d' % (j)) + ".tif"
        Lyr1 = QgsRasterLayer(Lyr1_path,"10km")
        Lyr2 = QgsRasterLayer(Lyr2_path,"0km")
        QgsMapLayerRegistry.instance().addMapLayers([Lyr1, Lyr2])
        entries = []
         
        boh1 = QgsRasterCalculatorEntry()
        boh1.ref = 'boh1@1'
        boh1.raster = Lyr1
        boh1.bandNumber = 1
        entries.append(boh1)
         
        boh2 = QgsRasterCalculatorEntry()
        boh2.ref = 'boh2@1'
        boh2.raster = Lyr2
        boh2.bandNumber = 1
        entries.append(boh2)
         
        # Process calculation with input extent and resolution
        calc = QgsRasterCalculator('( boh2@1 >= 0 ) * 100 + ( boh1@1 > 0 )*( (-0.01) * boh1@1 + 100 )', res, 'GTiff', Lyr1.extent(), Lyr1.width(), Lyr1.height(), entries)
        m = calc.processCalculation()
        result = QgsRasterLayer(res,"res")
        QgsMapLayerRegistry.instance().addMapLayer(result)
        QgsMapLayerRegistry.instance().removeAll

print("done!")