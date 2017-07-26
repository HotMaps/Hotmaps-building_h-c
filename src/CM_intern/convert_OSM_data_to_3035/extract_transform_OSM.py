# --------------------------------------- Header -------------------------------------------------

import os
import sys

import zipfile
from Cython.Compiler.Nodes import PassStatNode


from contextlib import  closing


import sys, os, shutil, time




# ------------------------------------------------------------------------------------------------------------
# --------------------------------------- Additional imports -------------------------------------------------

sys.path.insert(0, "../../")

import CM_intern.common_modules.reprojection as rp
"""

import EnergyDensity
from EnergyDensity.extent import Layer_Extent


"""

# Defines whether or not a new layer of Municipality borders is used 
#

NEW_commun_lyr_data = False

#
##################


"""

get_Landuse = True
if get_Landuse == True:
    building_data_np_file = "LandUseData.npz"
    lyr_zip_name = "landu"
    code_ = [7203,7204,7209,7212]
else:
    lyr_zip_name = "build"
    building_data_np_file = "BuildingData.npz"
    code_ = []
"""
#identifier = lyr_zip_name

commun_data_np_file = "CommunData.npz"


'''
        
def prepare_Commun_Layer(extent_lyr, commun_lyr, output_path):
    
    """ Run through commun_layer, check if its within rectengular extent layer 
        and get min/max coordinates of commun layer
        
    """
    for feature0 in extent_lyr.getFeatures():
        break
        
    
    
    print("Run Municipality - layer")
    geom0 = feature0.geometry()
    
    st = time.time()
        
    BoxCoord = np.zeros((4,2),'f8')

    Features_Commun = []
    
    CommunID = np.zeros((commun_lyr.featureCount(),2), "uint32")    
    CommunID[:, 0] = np.arange(commun_lyr.featureCount())
    MinCoord = np.zeros((commun_lyr.featureCount(), 2), "f8")
    MaxCoord = np.zeros_like(MinCoord)
    AreaCommun = np.zeros((commun_lyr.featureCount()), "f8")

    k = -1
    i = -1

    num_commun_feat = commun_lyr.featureCount()
    id = range(num_commun_feat)
    request = QgsFeatureRequest().setFilterFids(id)
    for feature1 in commun_lyr.getFeatures(request):
        geom1 = feature1.geometry()
        
        i += 1
        if i % 20000 == 0:
            print ("%5.2f tds. (out of %5.2f)- Hits: %5.2f - %4.2f sec"%(i/1000.0,num_commun_feat/1000.0, k/1000.0, time.time() - st))
        if geom1.intersects(geom0):            
            k += 1
            #print i
            coords = feature1.geometry().boundingBox().asPolygon().split(",")
            for j in range(4):
                try:
                    BoxCoord[j, :] = map(float, coords[j].strip(" ").split(" "))
                except:
                    print "ALERT"
                    pass
                    #print coords
            
            MinCoord[k, :] = np.min(BoxCoord[:, :], axis=0)
            MaxCoord[k, :] = np.max(BoxCoord[:, :], axis=0)
            CommunID[k, 1] = i
            Features_Commun.append(feature1)
            AreaCommun[k] = geom1.area()
            
    

    MaxCoord = MaxCoord[:k+1, :]
    MinCoord = MinCoord[:k+1, :]
    CommunID = CommunID[:k+1, :]
    
    np.savez("%s/%s" % (output_path, commun_data_np_file), MinCoord, MaxCoord, CommunID, AreaCommun)
    
    if k < 0:
        print ("no intersecting commun layer found ")
        return(None, None, None, None)
    
    print ("Number of intersecting communs found: %i " % MaxCoord.shape[0])
    
    
    return (MinCoord, MaxCoord, CommunID, Features_Commun)
'''   
    
class ExtractAndTransformOSMData():
    
    def __init__(self, input_data_path, output_data_path
                 , data_path_exists=True):    
        
        print("Input Data Path: %s" % input_data_path)
        if not os.path.exists(input_data_path):
            print("Input Data Path doesn't exist")
            assert(os.path.exists(input_data_path))

        print("Output Data Path: %s" % output_data_path)
        if not os.path.exists(output_data_path):
            print("Data Path doesn't exist")
        
            if data_path_exists == True:
                assert(os.path.exists(output_data_path))
            else:
                os.makedirs(output_data_path)
        
        self.input_data_path = input_data_path
        self.output_data_path = output_data_path
        
        
        self._country_file_list = []
        for (dirpath, dirnames, filenames) in os.walk(self.input_data_path):
            for fn in filenames:
                if fn.endswith(".shp.zip"):
                    self._country_file_list.append(fn)
    
        print(self._country_file_list)
        
        self.OSM_input_feat_dict = {}
        self.OSM_input_feat_dict["landu"] = ["LandUseData.npz", [7203,7204,7209,7212]]
        self.OSM_input_feat_dict["build"] = ["BuildingData.npz", []]
        
        #self.buildings_input_feat = 'bb'
        
    
        
    
    
    def extract_and_reproject_files(self):
        counter = 0
        for file_ in sorted(self._country_file_list):
            counter +=1
            print("\n####################")
            print("FileNr. %i :   %s \n" %(counter, file_))

            file_ = "%s/%s" %(self.input_data_path, file_)
            NEW_SHAPE_FILE = self._check_files2extractAreproject(file_, self.OSM_input_feat_dict)
            
            if NEW_SHAPE_FILE == True:
                pass
                #break
            
    
    def _check_files2extractAreproject(self, file_, OSM_input_feat_dict):
        """
        extracts layers from zip file
        """
        input_base_name = os.path.basename(file_)
        country_id = input_base_name.split("-")[0]
        building_lyr_path_out2 = "%s/%s/" % (self.output_data_path, country_id)
        """
        # Test time difference between input and output directory (exists if not same machine)
        test_file_input = "%s/test.test" %(os.path.dirname(file_))
        test_file_output = "%s/test.test" %(self.output_data_path)
        open(test_file_input, 'a').close()
        open(test_file_output, 'a').close()
        mod_time_in = os.stat(test_file_input).st_mtime
        mod_time_out = os.stat(test_file_output).st_mtime
        
        TIME_DIFF = mod_time_in - mod_time_out
        os.remove(test_file_input)
        os.remove(test_file_output)
        """
        process_any_file = False
        if not os.path.exists(self.input_data_path):
            print("OSM lyr input file doesn't exist: %s" % self.input_data_path )
            return False
        
        mod_time_in = os.stat(file_).st_mtime
        print("    OSM - Data Download: %s" 
                  % time.strftime("%a, %d %b %Y %H:%M:%S", 
                                  time.localtime(mod_time_in)))
        # unzip Files
        building_lyr_file_out2_LIST = []
        with closing(zipfile.ZipFile(file_)) as zfile:
            # check if newer file available
            for info in zfile.infolist():
                for lyr_zip_name in OSM_input_feat_dict:
                    if lyr_zip_name in info.filename:
                        
                        building_lyr_file_out = ("%s/%s" 
                                                % (building_lyr_path_out2
                                                , info.filename))
                        building_lyr_file_out3035 = (building_lyr_file_out[:-4] 
                                                     + "_3035" + building_lyr_file_out[-4:])
                        
                        process_file = True
                        if building_lyr_file_out.endswith(".cpg") == True: # Codex
                            continue
                        if os.path.exists(building_lyr_file_out3035):
                            mod_time_out = os.stat(building_lyr_file_out3035).st_mtime
                        else: 
                            mod_time_out = 0
                        
                        if mod_time_out < mod_time_in:
                            print("    Converted File:      %s" 
                                    % time.strftime("%a, %d %b %Y %H:%M:%S", 
                                                    time.localtime(mod_time_out)))
                            process_any_file = True
                            break
                    
                    if process_any_file == True:
                        break
                            
                        
            # Extract 
            if process_any_file == False :
                print("%s : Most recent data extracted" %input_base_name)
            else:             
                for info in zfile.infolist():
                    for lyr_zip_name in OSM_input_feat_dict:
                        if lyr_zip_name in info.filename:
                            
                            building_lyr_file_out = ("%s/%s" 
                                                    % (building_lyr_path_out2
                                                    , info.filename))
                            
                            if building_lyr_file_out.endswith("shp"): 
                                building_lyr_file_out2 = building_lyr_file_out
                                building_lyr_file_out2_LIST.append(building_lyr_file_out2)
                                print_outout = "  Extract: %s to \n     %s" %(info.filename, building_lyr_file_out)
                            
                                if mod_time_out > 0:
                                    print_outout += "\n" + "    File exists, but newer data are available"
                                else:
                                    print_outout += "\n" + "    File doesn't exists"
                                print(print_outout)
                            
                            # Exctract
                            zfile.extract(info, building_lyr_path_out2)


                                
        try:
            zfile.close()
        except:
            pass
        NEW_SHAPE_FILE = False
        
        
        if len(building_lyr_file_out2_LIST) > 0:
            for building_lyr_file_out2 in building_lyr_file_out2_LIST:
                building_lyr_file_out3 = building_lyr_file_out2.replace(".shp", "_3035.shp")    
                print("         Start reprojection of: %s" % building_lyr_file_out3)
                # Transformation of Layer CRS
                st = time.time()
                rp.reprojectShp2Shp(building_lyr_file_out2, building_lyr_file_out3)
                print("GDAL: %4.3f sec" %(time.time() - st))
                st = time.time()
                rp.reproject(building_lyr_file_out2, building_lyr_file_out3)
                print("Qgis: %4.3f sec" %(time.time() - st))
                NEW_SHAPE_FILE = True
                print("         New reprojected files: %s" % building_lyr_file_out3)
            """
            for (dirpath, dirnames,filenames) in os.walk(os.path.dirname(building_lyr_file_out3)):
                for fn in filenames:
                    if "_3035." in fn:
                        pass
                    else:
                        full_fn = "%s/%s" %(dirpath, fn)
                        full_fn_3035 = full_fn[:-4] + "_3035" + full_fn[-4:]
                        if os.path.exists(full_fn_3035):
                            try:
                                os.remove(full_fn)
                            except:
                                pass
            """
            return NEW_SHAPE_FILE
        
        
        
'''     
#@profile
def main(country_shape_file):

    pass
    
    start_time = time.time()
    buildings_input_feat = "bb"
    
    
    building_lyr_file = "%s/%s" %(building_lyr_base_path, country_shape_file)
    building_lyr_file_out = building_lyr_path2
    
    
    building_lyr_file_out, NEW_building_data = get_building_def_shape_file(building_lyr_file
                                                    , building_lyr_file_out
                                                    , buildings_input_feat)
    
    output_path = os.path.dirname(building_lyr_file_out)
    print output_path
    
    if not os.path.exists(building_lyr_file_out):        
        print( "Error preparing building layer file")
        return
    else:
        print ("Building data extracted")
    
    
    
    building_lyr_path = building_lyr_file_out
    print ("Load buildings layer")
    building_lyr = QgsVectorLayer(building_lyr_path,"bb","ogr")
    print "Create Extent Layer"
    Layer_Extent(building_lyr_path,extent_lyr_path)
    print "Load Extent Layer"
    extent_lyr = QgsVectorLayer(extent_lyr_path,"extent","ogr")

    
    print ("Load commun layer")
    commun_lyr = QgsVectorLayer(commun_lyr_path,"commun","ogr")
    print ("Done")

    
    
    (MinCoord, MaxCoord, CommunID, Features_Commun) = prepare_Commun_Layer(extent_lyr, commun_lyr, output_path)
    
    if MinCoord == None:
        return
    
    
    print "Run Building - layer"
    
    print "Number of Features (buildings): %i" % building_lyr.featureCount()
    BUIDLINGS_RESULTS = np.zeros((building_lyr.featureCount(), 4), dtype="f8") 
    BUIDLINGS_RESULTS[:,0] = -1
    
    
    try:
        
        BUIDLINGS_RESULTS_prev = np.load("%s/%s" % (output_path, building_data_np_file))['arr_0']
        #"""
        
        max_row = np.minimum(BUIDLINGS_RESULTS_prev.shape[0], BUIDLINGS_RESULTS.shape[0])
        max_col = np.minimum(BUIDLINGS_RESULTS_prev.shape[1], BUIDLINGS_RESULTS.shape[1])
        BUIDLINGS_RESULTS[:max_row, :max_col] = BUIDLINGS_RESULTS_prev[:max_row, :max_col]
                                                                                                    
        """
        BUIDLINGS_RESULTS2 = BUIDLINGS_RESULTS_prev[:, -1]
        import matplotlib.pyplot as plt
        cmap = plt.get_cmap('jet')
        
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(9, 4))
        
        sort_BUIDLINGS_RESULTS = np.sort(BUIDLINGS_RESULTS2)
        #plo = plt.plot(np.cumsum(sort_BUIDLINGS_RESULTS),sort_BUIDLINGS_RESULTS)
        #plo = plt.plot(np.arange(sort_BUIDLINGS_RESULTS.shape[0]), np.cumsum(sort_BUIDLINGS_RESULTS))
        plo = plt.plot(sort_BUIDLINGS_RESULTS, np.cumsum(sort_BUIDLINGS_RESULTS)/ np.sum(sort_BUIDLINGS_RESULTS))
        plt.show()
        """
    except:
        pass
    
    
    
    
    
    
    
    i = -1
    st = time.time()
    counter_false = 0
    prevCommun_ID = 0
    pre_existing_hits = 0
    
    BuildAreaCommun = np.zeros((MinCoord.shape[0]))
    BuildCommun = np.zeros((MinCoord.shape[0]))

    num_build_feat = building_lyr.featureCount()
    HIT = 0
    NOHIT = 0
    
    # the field code contains inforamtion of type of feature (building, residential area, grassland, etc)
    curcode_idx = building_lyr.fieldNameIndex("code")
    
    for feature2 in building_lyr.getFeatures():
        flag = 0
        
        i += 1
        #if i > 4000:
        #    break
        
        geom2 = feature2.geometry()
        
        if BUIDLINGS_RESULTS[i, 1] > 0:
            #Check if some data already exist
            if NEW_commun_lyr_data == False:
                if NEW_building_data == False:
                    flag = 2
                    
                elif geom2.area() == BUIDLINGS_RESULTS[i, 2]:
                    flag = 2
            if flag == 2:
                
                try:
                    _Commun_ID = CommunID[CommunID[:,1] == int(BUIDLINGS_RESULTS[i, 1]), 0][0]
                    HIT += 1
                    pre_existing_hits += 1
                    
                except:
                    #print ("Commun_ID not found")    
                    NOHIT += 1
                    flag = 0
        
        
        #flag = 0
        if flag == 0:
            geom1 = Features_Commun[prevCommun_ID].geometry()
            if geom2.intersects(geom1):
                #First shot: Try same commun as before    
                flag = 1
                _Commun_ID = prevCommun_ID
            
        if flag == 0:
            try:
                x,y = geom2.asPolygon()[0][0]
                #print ("%f %f" %(x,y))
            except:
                print geom2.asPolygon()
                continue
            idx1 = np.logical_and(x >= MinCoord[:, 0], x <= MaxCoord[:, 0])
            idx1 = np.logical_and(idx1, y >= MinCoord[:, 1])
            idx1 = np.logical_and(idx1, y <= MaxCoord[:, 1])
            Commun_ID = list(CommunID[idx1, 0])

            for id in Commun_ID:
                #print time() - st
                geom1 = Features_Commun[id].geometry()
                if geom1.intersects(geom2):
                    flag = 1
                    _Commun_ID = id
                    prevCommun_ID = id
                    break
                    

        if flag >= 1:
            prevCommun_ID = _Commun_ID    
            # set original Running Number and Commun_ID 
            BUIDLINGS_RESULTS[i, :2] = CommunID[_Commun_ID, :]    
        
        if flag >= 1:
            Area = float(geom2.area())
            BUIDLINGS_RESULTS[i, 2] = Area    
            
            
            curcode = feature2.attributes()[curcode_idx]
            if len(code_) == 0 or curcode in code_:
                BUIDLINGS_RESULTS[i, 3] = curcode
                BuildAreaCommun[_Commun_ID] += Area
                if Area > 50:
                    BuildCommun[_Commun_ID] += 1.0
            
        if flag == 0:
            counter_false += 1
        if i% 10000 == 0:
            print ("%5.2f tds. (out of %5.2f tds.)- NoHits: %i - NewHits: %4.3f tds.  - %4.2f sec"%(i/1000.0,num_build_feat/1000.0, counter_false, (i - counter_false - pre_existing_hits + 1) / 1000.0, time.time() - st))
            #print HIT
            #print NOHIT
        if i% 100000 == 0:
            np.savez("%s/%s" % (output_path, building_data_np_file), BUIDLINGS_RESULTS)
            
            
    print "Buildings: Hits %i, no commun found: %i" %(i - counter_false, counter_false)
        
    print time.time() - start_time
    
    
    #"""
    XX = np.load("%s/CommunData.npz" % output_path)
    MinCoord = XX['arr_0']
    MaxCoord = XX['arr_1']
    CommunID = XX['arr_2']
    AreaCommun = XX['arr_3']
    
    try:
        BuildCommun
    except:
        BuildAreaCommun = XX['arr_4']
        BuildCommun = XX['arr_5']
    
    idx = BuildAreaCommun[:] > 0
    
    MinCoord = MinCoord[idx]
    MaxCoord = MaxCoord[idx]
    AreaCommun = AreaCommun[idx]
    BuildCommun = BuildCommun[idx]
    BuildAreaCommun = BuildAreaCommun[idx]
    CommunID = CommunID[idx]
    
    np.savez("%s/%s" % (output_path, commun_data_np_file) , MinCoord, MaxCoord, CommunID, AreaCommun, BuildAreaCommun, BuildCommun)
    np.savez("%s/%s" % (output_path, building_data_np_file), BUIDLINGS_RESULTS)
        
    print np.sum(BuildAreaCommun, axis = 0)
    print np.sum(BUIDLINGS_RESULTS[BUIDLINGS_RESULTS[:,0] >= 0], axis = 0)
        
    
    

    
    
    
    build_area_exist = False
    build_number_exist = False
    commun_area_exist = False
    vpr = commun_lyr.dataProvider()
    
    for i in vpr.attributeIndexes():
        if commun_lyr.attributeDisplayName(i).lower() == "%s_area" % identifier:
            build_area_exist = True
            fieldname_build_area = commun_lyr.attributeDisplayName(i)
            build_area_index = i
        elif commun_lyr.attributeDisplayName(i).lower() == "%s_numb" % identifier:
            build_number_exist = True
            fieldname_build_numb = commun_lyr.attributeDisplayName(i)
            build_number_index = i
        elif commun_lyr.attributeDisplayName(i).lower() == "commu_area":
            commun_area_exist = True
            fieldname_commun_area = commun_lyr.attributeDisplayName(i)
            commun_area_index = i
            

    if build_number_exist == False:
        vpr.addAttributes([QgsField("%s_numb" % identifier, QVariant.Double)]) 
        build_number_index = vpr.attributeIndexes()[-1]
        fieldname_build_numb = "%s_numb" % identifier
    if build_area_exist == False:
        vpr.addAttributes([QgsField("%s_area" % identifier, QVariant.Double)]) # in square-meter
        fieldname_build_area = "%s_area" % identifier
        build_area_index = vpr.attributeIndexes()[-1]
    if commun_area_exist == False:
        vpr.addAttributes([QgsField("commu_area", QVariant.Double)]) # in square-meter
        fieldname_commun_area = "commu_area"
        commun_area_index = vpr.attributeIndexes()[-1]
        
        
    """    

    build_number_index = commun_lyr.fieldNameIndex(fieldname_build_numb)    
    build_area_index = commun_lyr.fieldNameIndex(fieldname_build_area)    
    commun_area_index = commun_lyr.fieldNameIndex(fieldname_commun_area)    
    """
    
    commun_lyr.updateFields()
    
    
    request = QgsFeatureRequest().setFilterFids(list(CommunID[:,1]))
    
    for i, feature1 in enumerate(commun_lyr.getFeatures(request)):
        commun_lyr.startEditing()
        print i
        fid1 = feature1.id()
        fid1_int = np.int(fid1)
        if fid1_int == CommunID[i, 1]:
            j = i
        else:
            j = np.argmax(CommunID[:, 1] == fid1_int)
        
        
        
        feature1.setAttribute(build_area_index, float(BuildAreaCommun[j]))
        feature1.setAttribute(build_number_index, float(BuildCommun[j]))
        feature1.setAttribute(commun_area_index, float(AreaCommun[j]))
        
        
        commun_lyr.changeAttributeValue(fid1, build_area_index, float(BuildAreaCommun[j]))
        commun_lyr.changeAttributeValue(fid1, build_number_index, float(BuildCommun[j]))
        commun_lyr.changeAttributeValue(fid1, commun_area_index, float(AreaCommun[j]))
        
        commun_lyr.updateFeature(feature1)
        
    commun_lyr.commitChanges()
        
    #QgsVectorFileWriter.writeAsVectorFormat(commun_lyr, commun_lyr_path.replace(".shp", "_NEW.shp"), "CP1250", None, "ESRI Shapefile")
    
    
    
    
    elapsed_time = time.time() - start_time
    print(elapsed_time)
    
    
    #app.exitQgis()
if __name__ == "__main__":

    for country in country_file_list[:]:
        
        
        if 1== 1:
            print country
            main(country)
            
    '''
