'''
Created on Jul 24, 2017

@author: Andreas

run this script to calculate the energy density maps
'''

import sys
from leach_osm_geofabrik import LeachOSMFilesFromGeofabrik




if __name__ == "__main__":
    
    print(sys.version_info)
    data_path = "/home/simulant/ag_lukas/personen/Andreas/Openstreetmapdata"
    
    # Prepare
    LOSMF = LeachOSMFilesFromGeofabrik(data_path)
    
    # Call method to add new urls to Data File
    # LOSMF.request_urls(check_size=False)

    # each online file size is a request, the total daily number of request is limited to about 40
    LOSMF.check_size_online_file(range(20))
    LOSMF.print_URLcollectionData()
    IndexListOfDownloads = LOSMF.determine_most_urgent_downloads(20)
    # each download is a request, the total daily number of request is limited to about 40
    #LOSMF.download_OSM_files(IndexListOfDownloads[:])
    print("Done!")

