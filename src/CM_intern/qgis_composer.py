from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import numpy as np
import pandas as pd
import math


def logo_composer(c, logoPath, magnify_xy= (26.86, 8.5), xy_position= (22, 165.7)):
    composerLogo = QgsComposerPicture(c)
    composerLogo.setPictureFile(logoPath)
    composerLogo.setSceneRect(QRectF(0,0,magnify_xy[0],magnify_xy[1]))
    composerLogo .setItemPosition(xy_position[0], xy_position[1])
    c.addItem(composerLogo)

def scalebar_composer(c, composerMap, xy_position, font, font_size):
    # create scale bar
    composerScalebar = QgsComposerScaleBar(c)
    composerScalebar.setComposerMap(composerMap)
    composerScalebar.setStyle('Line Ticks Up') # Other possibilities are: 'Single Box', 'Double Box', 'Line Ticks Middle', 'Line Ticks Down', 'Line Ticks Up', 'Numeric'
    composerScalebar.applyDefaultSize()
    composerScalebar.setNumSegments(1)
    composerScalebar.setNumSegmentsLeft(0)
    composerScalebar.setNumMapUnitsPerScaleBarUnit(1000)
    composerScalebar.setUnitLabeling("km")
    composerScalebar.setHeight(1)
    composerScalebar.setLabelBarSpace(1)
    f1 = QFont( font, font_size )
    composerScalebar.setFont(f1)    
    composerScalebar.setItemPosition(xy_position[0], xy_position[1])
    c.addItem(composerScalebar)



def label_composer(c, text_content, font, font_size, bold,
    (r, g, b), x, y, alignbool=False):
    f1 = QFont( font, font_size )
    f1.setBold(bold)
    if "change" in text_content:
        temp = text_content.split(",")
        text1 = temp[0] + ',' + temp[1] + ',' + temp[2] + ','
        text2 = temp[3] + ',' + temp[4]
        temp = [text2, text1]
        for i in range(2):
            composerLabel = QgsComposerLabel(c)
            composerLabel.setFont(f1)
            composerLabel.setFontColor(QColor.fromRgb(r, g, b))
            composerLabel.setText(temp[i])
            composerLabel.setItemPosition(x-(1-i), y+ 2.5*pow(-1,i), 0, 0, QgsComposerItem.UpperLeft, False, 0)
            composerLabel.adjustSizeToText()
            composerLabel.setFrameEnabled(False)
            c.addItem(composerLabel)
    else:
        composerLabel = QgsComposerLabel(c)
        composerLabel.setFont(f1)
        composerLabel.setFontColor(QColor.fromRgb(r, g, b))
        composerLabel.setText(text_content)
        composerLabel.setItemPosition(x, y, 0, 0, QgsComposerItem.UpperLeft, False, 0)
        composerLabel.adjustSizeToText()
        composerLabel.setFrameEnabled(False)
        c.addItem(composerLabel)


def legend_composer(c, layerGroup, legendTitle, fonts , font_sizes, xy_position, set_bold = False, set_background = False):
    '''
    f1: titleFont
    f2: subGroupFont
    f3: symbolLabelFont
    '''
    f0 =  QFont(fonts[0], font_sizes[0])
    f1 =  QFont(fonts[1], font_sizes[1])
    f2 =  QFont(fonts[2], font_sizes[2])
    f0.setBold(set_bold)
    f1.setBold(set_bold)
    f2.setBold(set_bold)
    legend = QgsComposerLegend(c)
    legend.modelV2().setRootGroup(layerGroup)
    legend.setTitle(legendTitle)
    legend.setStyleFont(QgsComposerLegendStyle.Title, f0)
    legend.setStyleFont(QgsComposerLegendStyle.Subgroup, f1)
    legend.setStyleFont(QgsComposerLegendStyle.SymbolLabel, f2)
    legend.setItemPosition(xy_position[0], xy_position[1], itemPoint=legend.UpperLeft)
    legend.setBackgroundEnabled(set_background)
    c.addItem(legend)


def renderMap(map_title, map_footer, logoPath, output):
    if os.path.isfile(output):
        os.remove(output)
    # zoom to extent and refresh the canvas
    layers = iface.legendInterface().layers()
    vLayer = layers[len(layers)-1]
    canvas = iface.mapCanvas()
    extent = vLayer.extent()
    canvas.setExtent(extent)
    #qgis.utils.iface.mapCanvas().freeze(False)
    qgis.utils.iface.mapCanvas().refresh()
    proj = QgsProject.instance()
    reg = QgsMapLayerRegistry.instance()

    lyrs = []
    for i in iface.mapCanvas().layers():
        item = i.id()
        lyrs.append(item)
    
    
    mapRenderer = canvas.mapRenderer()
    mapRenderer.setLayerSet(lyrs)
    
    rect = QgsRectangle(extent)
    rect.scale(1.15)
    mapRenderer.setExtent(rect)
    c = QgsComposition(mapRenderer)
    c.setPlotStyle(QgsComposition.Print)
    c.setPaperSize(210, 297)
    w, h = c.paperWidth() , c.paperHeight()
    x = (c.paperWidth() - w) / 2
    y = ((c.paperHeight() - h)) / 2
    composerMap = QgsComposerMap(c,x,y,w,h)
    composerMap.setNewExtent(rect)
    #composerMap.setFrameEnabled(True)
    c.addItem(composerMap)


    text_content = map_title
    font, font_size, bold = 'Arial', 10, True
    (r,g,b) = (28, 62, 149)
    xPosition , yPosition = 21, 10.5
    label_composer(c, text_content, font, font_size, bold, (r, g, b), xPosition, yPosition)

    text_content =  u"\u00a9 ESPON, 2017"
    font, font_size, bold = 'Arial', 8, True
    (r,g,b) = (0, 0, 0)
    xPosition , yPosition = 51, 167.5
    label_composer(c, text_content, font, font_size, bold, (r, g, b), xPosition, yPosition)
    text_content = ['Regional level: NUTS 3 (version 2013)',
                'Source: ESPON LOCATE, 2017',
                map_footer,
                'CC - UMS RIATE for administrative boundaries']
    y_offset = 0
    x_offset = np.array([8.1, 12.4, -2.5, 1.2])-1
    x_offset1 = np.array([8.1, 12.4, -5.4, 1.2])-1
    font, font_size, bold = 'Arial', 5.5, False
    (r,g,b) = (0, 0, 0)
    for i, item in enumerate(text_content):
        if map_footer == "Origin of data: Eurostat 2001-2016, own calculations":
            xPosition , yPosition = 149 + x_offset[i], 174.5+y_offset
        else:
            xPosition , yPosition = 149 + x_offset1[i], 174.5+y_offset
        y_offset += 2
        label_composer(c, item, font, font_size, bold, (r, g, b), xPosition, yPosition, True)

    layerGroup = QgsLayerTreeGroup()
    layerGroup.insertLayer(0, layers[17])
    layerGroup.insertLayer(0, layers[13])
    layerGroup.insertLayer(0, layers[2])
    legendTitle = ""
    fonts = ('Arial','Arial','Arial')
    font_sizes = (8, 8, 6)
    xy_position = (19, 45)
    legend_composer(c, layerGroup, legendTitle, fonts , font_sizes, xy_position, False, False)
    
    xy_position = (158, 160)
    font = 'Arial'
    font_size = 6
    scalebar_composer(c, composerMap, xy_position, font, font_size)
    
    xy_position = (22, 165.7)
    magnify_xy = (26.86, 8.5)
    logo_composer(c, logoPath, magnify_xy, xy_position)
    
    dpi = c.printResolution()
    dpmm = dpi / 25.4
    width = int(dpmm * c.paperWidth())
    height = int(dpmm * c.paperHeight())

    # create output image and initialize it
    image = QImage(QSize(width, height), QImage.Format_ARGB32)
    image.setDotsPerMeterX(dpmm * 1000)
    image.setDotsPerMeterY(dpmm * 1000)
    image.fill(0)

    # render the composition
    imagePainter = QPainter(image)
    sourceArea = QRectF(0, 0, c.paperWidth(), c.paperHeight())
    targetArea = QRectF(0, 0, width, height)

    c.render(imagePainter, targetArea, sourceArea)
    imagePainter.end()
    image.save(output, "png")
    del(c)
    '''
    img = Image.open(output)
    print(img.size)
    img2 = img.crop((600, 810, 1870, 2040))
    img2.save(output[:-4]+'new.JPG')
    '''

def validatedDefaultSymbol( geometryType ):
    symbol = QgsSymbolV2.defaultSymbol( geometryType )
    if symbol is None:
        if geometryType == QGis.Point:
            symbol = QgsMarkerSymbolV2()
        elif geometryType == QGis.Line:
            symbol =  QgsLineSymbolV2 ()
        elif geometryType == QGis.Polygon:
            symbol = QgsFillSymbolV2 ()
    return symbol
    
    
def applyGraduatedSymbologyStandardMode( layer, field, classes, mode, legendFormat, precision):
    colorClassesHex = {4: {'color1': '#f0f9e8', 'color2': '#2b8cbe', 'stops': "0.3333;#bae4bc:0.6667;#7bccc4"},
                                5: {'color1': '#f0f9e8', 'color2': '#0868ac', 'stops': "0.25;#bae4bc:0.50;#7bccc4:0.75;#43a2ca"},
                                6: {'color1': '#f0f9e8', 'color2': '#0868ac', 'stops': "0.2;#ccebc5:0.4;#a8ddb5:0.6;#7bccc4:0.8;#43a2ca"},
                                7: {'color1': '#f0f9e8', 'color2': '#08589e', 'stops': "0.16667;#ccebc5:0.33334;#a8ddb5:0.5;#7bccc4:0.66667;#4eb3d3:0.83334;#2b8cbe"},
                                8: {'color1': '#f7fcf0', 'color2': '#08589e', 'stops': "0.142857;#e0f3db:0.285714;#ccebc5:0.428571;#a8ddb5:0.571429;#7bccc4:0.714286;#4eb3d3:0.857143;#2b8cbe"}, 
                                9: {'color1': '#f7fcf0', 'color2': '#084081', 'stops': "0.125;#e0f3db:0.25;#ccebc5:0.375;#a8ddb5:0.5;#7bccc4:0.625;#4eb3d3:0.75;#2b8cbe:0.875;#0868ac"}}
    
    symbol = validatedDefaultSymbol( layer.geometryType() )
    #colorRamp = QgsVectorGradientColorRampV2.create({'color1':'255,0,0,255', 'color2':'0,0,255,255','stops':'0.25;255,255,0,255:0.50;0,255,0,255:0.75;0,255,255,255'})
    colorRamp = QgsVectorGradientColorRampV2.create(colorClassesHex[classes])
    mylegendFormat = QgsRendererRangeV2LabelFormat()
    mylegendFormat.setPrecision(precision)
    mylegendFormat.setFormat(legendFormat)
    renderer = QgsGraduatedSymbolRendererV2.createRenderer( layer, field, classes, mode, symbol, colorRamp, legendFormat = mylegendFormat )
    #renderer.setSizeScaleField("LABELRANK")
    layer.setRendererV2( renderer )


def GraduateModes(layer, mapTitle, targetField, dataOrigin, classes, legendFormat, precision, mode):
    modes = { QgsGraduatedSymbolRendererV2.EqualInterval : "Equal Interval",
          QgsGraduatedSymbolRendererV2.Quantile: "Quantile",
          QgsGraduatedSymbolRendererV2.Jenks: "Natural Breaks (Jenks)",
          QgsGraduatedSymbolRendererV2.StdDev: "Standard Deviation",
          QgsGraduatedSymbolRendererV2.Pretty: "Pretty Breaks"
        }
    if layer.isValid():
        applyGraduatedSymbologyStandardMode(layer, targetField, classes, modes.keys()[mode], legendFormat, precision)
        QgsMapLayerRegistry.instance().addMapLayers( [layer] )
    output = "C:/Users/Mostafa/Desktop/Espon/"+targetField+".png"
    logoPath = "C:/Users/Mostafa/Desktop/Espon/logo.svg"
    renderMap(mapTitle, dataOrigin, logoPath, output)


input_file = "Z:/personen/Mostafa/ESPON/map_properties.csv"
ifile = pd.read_csv(input_file)
mapTitles = ifile['Title'].values.astype(str)
targetField = ifile['Field'].values.astype(str)
dataOrigin = ifile['Origin'].values.astype(str)
classes = ifile['Legend_Classes'].values.astype(int)
legendFormat = ifile['Legend_Format'].values.astype(str)
precision = ifile['Precision'].values.astype(int)
mode = ifile['Mode'].values.astype(int) #1: Quantile

layers = iface.legendInterface().layers()
layer = layers[2]
for i in range(30):
    GraduateModes(layer, str(mapTitles[i]), str(targetField[i]), str(dataOrigin[i]), int(classes[i]), str(legendFormat[i]), int(precision[i]), int(mode[i]))
        
    