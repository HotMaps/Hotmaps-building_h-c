# -*- coding: iso-8859-15 -*-
'''
Created on 29.04.2014

@author: andreas
'''
import requests 
import zipfile

#import urllib
from bs4 import BeautifulSoup
import time

import os
import random
import base64
import numpy as np
import pickle
#import datetime
import sys

if sys.version_info[0] == 2:
    import urllib2 as urllib2
else:
    import urllib.request as urllib2

TIME_TO_WAIT = 0
username="YYYY"
password = "XXXX"

BASE_LINK = "http://download.geofabrik.de/"
main_link = "http://download.geofabrik.de/europe.html"


# check geofabrik for urls/new urls
request_urls = False
# geofabrik allows only 40 request per day
MaxNumDownloads = 35

# check online size of data file (counts as one request!)
#check_download_size = True
#number of checks for online size -> if there is a very recent size check then not needed
MaxNumSizeCheck = 20

# if true perform actual download
TEST_SYSTEM = False


FN_FINAL_DOWNLOAD_LIST = "geofabrik_download_list.pk" 
FN_GEOFABRIK_LINKS = "geofabrik_links_short.txt"

##################################
#
#
#################################
def scrapper(string, country, wait_factor=0
             , return_links=True
             , full_list = [], check_size=False):
    #
    #print(string)
    
    a = random.random()
    wait_time = a*wait_factor
    #print("wait %3.1f sec: " % wait_time)
    time.sleep(wait_time)
    
    request = urllib2.Request(string.replace(" ", "%20"))
     
    auth_required=False
    if auth_required == True:
        if 0 ==1:
            r = requests.get(string.replace(" ", "%20"), auth=(username, password))
        if 1==1:
            base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)   
    
    #try:
    if 1==1:    
        url = urllib2.urlopen(request)
        content = url.read() 
        
        f = open("%s%s" % ("", "test.html"), 'wb')
        f.write(content)
        f.close()
        soup = BeautifulSoup(content, "html5lib")
        links = (soup.findAll("a"))
        links_list = []
        for l in links:
            #print l
            #if str(l).startswith('<a href="europe/') and ".html" in str(l):
            if "-latest-free.shp.zip" in str(l):
                target_url = BASE_LINK + "europe/" + str(l).split('"')[1]
                if target_url not in links_list:
                    if target_url not in full_list:
                        links_list.append(target_url)
        
        
        f = open("%s%s" % ("", "links.txt"), 'a')
        for l in links_list:
            f.write(str(l) + "\n")
        f.close()
        
        if len(links_list) > 1:
            add_country = country.lower() + "_"
        else:
            add_country = ""
        
        links_and_names = []
        for l in links_list:
            target_file_name = l.split("/")[-1].split("-latest-free")[0].replace("-", "_")
            target_file_name += "-latest-free.shp.zip"
            
            if check_size == True:
                size_, XX = get_site_info(l)
            else:
                size_ = -1
            links_and_names.append([l, add_country + target_file_name, float(size_)])
            
        try:
            os.remove("%s%s" % ("", "test.html"))
            os.remove("%s%s" % ("", "links.txt"))
        except:
            pass
        return (links_and_names)
    """
    except:
        print "\n999999999999999999999\nE R R O R"
        print string
        return []
    """
###########################
def get_site_info(url_):
    site = urllib2.urlopen(url_)
    meta = site.info()
    try:
        size_ = meta.getheaders("Content-Length")[0]
    except:
        size_ = meta.get("Content-Length")
    return size_, meta
    

###########################

def test_link(link, wait_factor= 0):
    
    request = urllib2.Request(link)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    a = random.random()
    wait_time = a * wait_factor
    #print ("wait %3.1f sec: " % wait_time)
    print (link +" ::    wait %3.1f sec: " % wait_time)
    time.sleep(wait_time)
    try:
        url = urllib2.urlopen(request)
        return True
    except Exception as e:
        if e.reason == "Forbidden":
            print("\n--------------\nFORBIDDEN: " + link + "\n--------------\n")
            return None
        else:
            return False




class LeachOSMFilesFromGeofabrik():

    def __init__(self, data_path, data_path_exists=True ):
        
        self.RequestCounter = 0 
        
        # Path were data are stored locally
        print("Data Path: %s" % data_path)
        if not os.path.exists(data_path):
            print("Data Path doesn't exist")
        
            if data_path_exists == True:
                assert(os.path.exists(data_path))
            else:
                os.makedirs(data_path)
            
        self.data_path = data_path
        
        fn_geofabrik_links = "./%s" %(FN_GEOFABRIK_LINKS)
        
        self.target_url_list = self._read_urls_fromfile(fn_geofabrik_links)
        assert(len(self.target_url_list) > 0)    
        
        self.fn_final_download_list = "%s/%s" %(self.data_path, FN_FINAL_DOWNLOAD_LIST)
        
        error_occured, tuple_  = self._load_bin_file(self.fn_final_download_list)
        
        if error_occured == False:
            self.FINAL_DOWNLOAD_LINKS = list(tuple_)
        else:
            self.FINAL_DOWNLOAD_LINKS = []
            
        #for data in self.FINAL_DOWNLOAD_LINKS:
        #    print(data[1])
        print ("Total Links: %i" % len(self.FINAL_DOWNLOAD_LINKS))
    
        self._check_size_and_date_local_file() 
    
        return
        
     
    def _read_urls_fromfile(self, filename):
    
        target_url_list = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for l in f.readlines():
                    #print l
                    target_url = BASE_LINK + "/" + l.split('"')[1]
                    #print target_url
                    country = l.split('">')[1].split("<")[0].replace("-","_").replace(" ","_")
                    target_url_list.append((target_url, country))
            f.close()  
        else:
            print("file with URLs doesn't exists: %s" % filename)  
        return target_url_list
    
    def _load_bin_file(self, filename):
        """
            Reads data from binary file
            Returns DATA
        """
        
        error_occured = False
        if os.path.exists(filename) == False:
            DATA = tuple()
            print("file %s doesnt exits" % filename)
            error_occured = True
        else:
            try:
                with open(filename, 'rb') as input:  
                    DATA = pickle.load(input)  
            except Exception as e:
                print(e)
                error_occured = True
            finally:
                try:
                    input.close()
                except: 
                    pass  
        if error_occured == True:
            print("Cannot read existing file: %s " % filename) 
            print("Check Python version 2/3?. Abort run --> End: ") 
            sys.exit()
        return (error_occured
                , DATA)
        
    def _dump_bin_file(self, filename, DATA
                       , check=True):
        """
        Receives data as tuple (?)
        writes the data to binary file
        """
        
        error_occured = False
        
        time.sleep(0.5)
        new_file_name = ""
        if os.path.exists(filename) and os.path.isfile(filename):
            new_file_name = ("%s_%s.%s" % (filename[:-3]
                                , time.strftime("%Y_%d %b %H-%M-%S", 
                                  time.localtime(time.time())) 
                                , filename[-2:]))
            try:
                os.rename(filename, new_file_name)
            except:
                print("Copying file: %s failed" % new_file_name)

            
        try:
            fn_dummy = filename + "_dummy"
            with open(fn_dummy, 'wb') as output:           
                pickle.dump(DATA, output, protocol = 2)
        except:
            error_occured = True
        finally:
            try:
                output.close()
            except: 
                pass  
        time.sleep(1) 
        
        if error_occured == False and check == True:
            (error_occured, DATA) = self._load_bin_file(fn_dummy)
            
            
        if error_occured == False and os.path.exists(fn_dummy):
            new_size = os.stat(fn_dummy).st_size

            if new_file_name != "" and os.path.exists(new_file_name):
                old_size = os.stat(new_file_name).st_size
            elif os.path.exists(filename):
                old_size = os.stat(filename).st_size
            else:
                old_size = 0
            
            if new_size >= 0.8 * old_size:
                if os.path.exists(filename):
                    try:
                        os.rename(filename, new_file_name)
                    except:
                        os.remove(filename)
                try:
                    os.rename(fn_dummy, filename)
                except:
                    error_occured = True
                    
                    
                    
        if error_occured == True:
            print("\n\n\n  Creating file: %s failed ")
            print("Abort process\n   -> End")
            sys.exit()
         
        return (error_occured)
    
    
    def request_urls(self, check_size=False):
        for li, country in self.target_url_list:
                
            link_ = "%s" %(li) 
            #############
            # Aufruf scrapper 
            
            #full_list contains all already existing links
            # Used to check whether or not link is already part of 
            # existing links collection
            full_list = []
            for X in self.FINAL_DOWNLOAD_LINKS:
                full_list.append(X[0])
                
            links = scrapper(link_, country, TIME_TO_WAIT
                             , full_list=full_list, check_size=check_size)
            
            if type(links) is list and len(links) > 0:
                for ele in links:
                    (url_, fn, online_size) = ele
                    
                    print("New URL: %s" % url_)
                    if check_size == True:
                        date_size_check_online = time.time()
                    else:
                        date_size_check_online = 0
                    
                    self.FINAL_DOWNLOAD_LINKS.append([url_, fn, 0, 0, 0
                                , date_size_check_online, online_size])
        
        self._check_size_and_date_local_file()   
        error_occured = self._dump_bin_file(self.fn_final_download_list
                            , self.FINAL_DOWNLOAD_LINKS)
                
        
        return

    
    
    def _check_size_and_date_local_file(self):

        target_fn_list = []
        #modification_time = np.zeros((len(self.FINAL_DOWNLOAD_LINKS)))
        i = -1
        for tuple_ in self.FINAL_DOWNLOAD_LINKS:
            if len(tuple_) == 3:
                (url_, fn, local_size) = tuple_
                mod_time_local = 0
                size_online_last_download = 0
                date_size_check_online = 0
                size_online_latest = 0
            else:
                (url_, fn, mod_time_local, local_size, size_online_last_download
                , date_size_check_online, size_online_latest) = tuple_
            
            
            i += 1
            # Check filename
            fn2 = (fn.split("/")[-1].split("-latest-free")[0].replace("-", "_") + "-latest-free" + fn.split("/")[-1].split("-latest-free")[1]).lower()
            if fn2 != fn:
                print(fn2)
            
            #check if local file exists and check modification date    
            local_fn = '%s/%s'%(self.data_path, fn2)
            if os.path.exists(local_fn):
                mod_time_local = os.path.getmtime(local_fn) 
                statinfo = os.stat(local_fn)
                local_size = statinfo.st_size
                if size_online_last_download == 0:
                    size_online_last_download = local_size
            else:
                mod_time_local = 0
                local_size = 0
                size_online_latest = 0
            
            
            local_size = float(local_size)  
            if date_size_check_online < mod_time_local - 1000:
                date_size_check_online = mod_time_local - 1000
                
            self.FINAL_DOWNLOAD_LINKS[i] = (url_, fn2, mod_time_local, local_size, size_online_last_download
                                            , date_size_check_online, size_online_latest)

            target_fn_list.append(fn2)
               
        error_occured = self._dump_bin_file(self.fn_final_download_list
                                    , self.FINAL_DOWNLOAD_LINKS) 
                
        return
    
    def print_URLcollectionData(self):
        
        counter = 0
        for (url_, fn, mod_time_local, local_size, size_online_last_download
                , date_size_check_online, size_online_latest) in self.FINAL_DOWNLOAD_LINKS:
            counter += 1
            print("\n##################") 
            print("Nr. %i" %counter)
            self._print_URLcollectionData(url_, fn, mod_time_local, local_size, size_online_last_download
                , date_size_check_online, size_online_latest)
        return
    def _print_URLcollectionData(self, url_, fn, mod_time_local, local_size, size_online_last_download
                , date_size_check_online, size_online_latest):

            print("URL: %s" % url_)
            print("    Filename: %s" % fn)
            print("    Modtime local: %s" 
                  % time.strftime("%a, %d %b %Y %H:%M:%S", 
                                  time.localtime(mod_time_local)))
            print("        Local Size: %4.2f MB" % (local_size / 10**6))
            print("        Online Size Download: %4.2f MB" % (size_online_last_download / 10**6))
            print("    Time OnlineCheck: %s" 
                  % time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(date_size_check_online)))
            
            print("        Online Size Last Check: %4.2f MB" % (size_online_latest / 10**6))
         
    def check_size_online_file(self, INDEX_LIST, max_number_of_size_checks=MaxNumSizeCheck):
        """ 
            Check the online size of files specified by INDEX List of 
            self.FINAL_DOWNLOAD_LINKS List
            
        """

        for i in INDEX_LIST:
            if i >= len(self.FINAL_DOWNLOAD_LINKS):
                continue
            (url_, fn, mod_time_local, local_size, size_online_last_download
                , date_size_check_online, size_online_latest) = self.FINAL_DOWNLOAD_LINKS[i]
            
            print ("%s" % fn)
            print("    Last OnlineCheck: %s" 
                  % time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(date_size_check_online)))
            if date_size_check_online >= time.time() - 3600*24*4:
                print ("Skip!\n")
                continue
            if self.RequestCounter > max_number_of_size_checks:
                break
            else:
                size_, meta = get_site_info(url_)
            
            self.FINAL_DOWNLOAD_LINKS[i] = (url_, fn, mod_time_local, local_size
                                            , size_online_last_download
                                            , time.time(), float(size_))
                
            self.RequestCounter += 1
            
        error_occured = self._dump_bin_file(self.fn_final_download_list
                                        , self.FINAL_DOWNLOAD_LINKS) 
        return
        
        
        
    def determine_most_urgent_downloads(self, number_of_downloads=MaxNumDownloads):
        """
        
        
        """
        print("\n\n\n\n\n\n\n##############\n\n\n\nDetermine most important downloads")
        modification_time_arr = np.zeros(len(self.FINAL_DOWNLOAD_LINKS))
        size_latest_online_size_check_arr = np.zeros_like(modification_time_arr)
        size_online_download_arr = np.zeros_like(modification_time_arr)
        size_online_latest_arr = np.zeros_like(modification_time_arr)
        size_local_arr = np.zeros_like(modification_time_arr)
        IndexVtr = np.arange(len(self.FINAL_DOWNLOAD_LINKS))
        
        for i in range(len(self.FINAL_DOWNLOAD_LINKS)):
            (url_, fn, mod_time_local, local_size, size_online_last_download
                , date_size_check_online, size_online_latest) = self.FINAL_DOWNLOAD_LINKS[i]
            
            # Round time stamp to 2 days   
            modification_time_arr[i] = mod_time_local 
            size_latest_online_size_check_arr[i] = date_size_check_online
            
            size_online_download_arr[i] = size_online_last_download
            size_online_latest_arr[i] = size_online_latest
            size_local_arr[i] = local_size
            
        
        #Sort by local modification time
        sortIDX_mod_time = np.argsort(modification_time_arr)
        newest_download_time = sortIDX_mod_time[:number_of_downloads][-1]
        
        # include all downloads which have the same download time (+ 2 days)
        cutoff_time = modification_time_arr[newest_download_time] + 3600*24*2
        #Dont download file if has been done in the last 5 days
        cutoff_time = np.minimum(cutoff_time, time.time() - 3600*24*5)
        print("Cutoff date 2: %s" % time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(cutoff_time)))
        IDX = modification_time_arr <= cutoff_time
        
        # Reduce Index Vector
        IndexVtr = IndexVtr[IDX]
        if IndexVtr.size == 0:
            return []
        print(IndexVtr)
        # Calculate difference in Size
        abs_diff_online = np.maximum(0, size_online_latest_arr - size_online_download_arr)
        sortIDX_abs_diff_online = np.argsort(abs_diff_online[IndexVtr])
        
        rel_diff_online = abs_diff_online / (size_online_download_arr + 1)
        sortIDX_rel_diff_online = np.argsort(rel_diff_online[IndexVtr])
        
        abs_diff_local = np.maximum(0, size_online_latest_arr - size_local_arr)
        sortIDX_abs_diff_local = np.argsort(abs_diff_local[IndexVtr])
        
        rel_diff_local = abs_diff_local / (size_local_arr + 1)
        sortIDX_rel_diff_local = np.argsort(rel_diff_local[IndexVtr])
        
        DOWNLOAD_URGENCY_INDEX = np.zeros_like(IndexVtr)
        for ele in range(len(sortIDX_abs_diff_online)):
            DOWNLOAD_URGENCY_INDEX[sortIDX_abs_diff_online[ele]] += ele + 1
            DOWNLOAD_URGENCY_INDEX[sortIDX_rel_diff_online[ele]] += ele + 1
            DOWNLOAD_URGENCY_INDEX[sortIDX_abs_diff_local[ele]] += ele + 1
            DOWNLOAD_URGENCY_INDEX[sortIDX_rel_diff_local[ele]] += ele + 1
        
        sortIDX_DOWNLOAD_URGENCY_INDEX = np.argsort(-DOWNLOAD_URGENCY_INDEX)
        
        
        FINAL_DOWNLOAD_LINKS_IndexVtr_URGENCY = IndexVtr[sortIDX_DOWNLOAD_URGENCY_INDEX]
        FINAL_DOWNLOAD_LINKS_IndexVtr_URGENCY = FINAL_DOWNLOAD_LINKS_IndexVtr_URGENCY[:number_of_downloads]
        Total_download = 0
        Total_diff = 0
        for i in FINAL_DOWNLOAD_LINKS_IndexVtr_URGENCY:
            (url_, fn, mod_time_local, local_size, size_online_last_download
                , date_size_check_online, size_online_latest) = self.FINAL_DOWNLOAD_LINKS[i]
            
            online_size = np.maximum(size_online_last_download, size_online_latest)
            offline_size_diff = online_size - local_size 
            print("\n##############")
            print("    %s  -> %4.2f -> %4.1f %% -> %4.2f MB"% (fn
                                , online_size  / 10 **6
                                , np.minimum(999, offline_size_diff / online_size * 100) 
                                , offline_size_diff / 10 **6))
            self._print_URLcollectionData(url_, fn, mod_time_local, local_size, size_online_last_download
                                              , date_size_check_online, size_online_latest)
            
            
        
        
            Total_download += online_size / 10 **6
            Total_diff += float(offline_size_diff / 10 **6)
        print("\n##############")
        print("Total_download: %i Files - %6.1f MB   - Diff %6.1f MB" %(len(FINAL_DOWNLOAD_LINKS_IndexVtr_URGENCY), Total_download, Total_diff))
        print("##############\n")
        return FINAL_DOWNLOAD_LINKS_IndexVtr_URGENCY
        
        
        
    def download_OSM_files(self, index_list):
        """ 
            Actual Download of data
        """
        print ("\n\n\nDownload List\n\n\n")
        for idx in index_list:
            (url_, fn, mod_time_local, local_size, size_online_last_download
                , date_size_check_online, size_online_latest) = self.FINAL_DOWNLOAD_LINKS[idx]
            self._print_URLcollectionData(url_, fn, mod_time_local, local_size, size_online_last_download, date_size_check_online, size_online_latest)
        print ("\n\n\nStart Downloads\n")
        for idx in index_list:
            if self.RequestCounter >= MaxNumDownloads:
                break
            (url_, fn, mod_time_local, local_size, size_online_last_download
                , date_size_check_online, size_online_latest) = self.FINAL_DOWNLOAD_LINKS[idx] 
            
            #Don't download data within 4 days
            if mod_time_local >= time.time() - 3600*24*4:
                continue
            local_fn = '%s/%s'%(self.data_path, fn)
            if os.path.exists(local_fn + "_temp") and os.path.isfile(local_fn + "_temp"):
                try:
                    os.remove(local_fn + "_temp")
                except:
                    print("Cannot remove file: %s" % local_fn + "_temp")
                    continue
            self.RequestCounter += 1
            response = requests.get(url_, stream=True)
            size_online_latest = response.headers.get('content-length')
            if size_online_latest != None:
                size_online_latest = float(size_online_latest)
                print("\n Request Nr. %i --  Filename: %s, size: %4.2f MB (local file size: %4.2f MB)" % 
                      (self.RequestCounter, fn, size_online_latest / 10 ** 6, local_size / 10 ** 6))
              
            if  size_online_latest == None or size_online_latest < 1000:
                print("No data recevied")
                break
            else:
                date_size_check_online = time.time()    
                 
            with open(local_fn + "_temp", "wb") as f:
                
                print("Downloading %s" % local_fn + "_temp")

                if size_online_latest is None: # no content length header
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(size_online_latest)
                    for data in response.iter_content(chunk_size=int(size_online_latest / 10+10)):
                        dl += len(data)
                        f.write(data)
                        percent = int(100 * dl / total_length)
                        sys.stdout.write("  %2d%%" % percent)
                        sys.stdout.flush()
                    print("\n")
                    
            error_occured = False          
            try:
                if (os.stat(local_fn ).st_size  <= 0.8 * os.stat(local_fn + "_temp").st_size
                        or os.stat(local_fn + "_temp").st_size < 0.95 * size_online_latest):
                    error_occured = True
                    print("Downloaded file is to small (%s)" % (local_fn + "_temp"))
            
                testopen = zipfile.ZipFile(local_fn + "_temp", 'r')
                try:
                    testopen.close()
                except:
                    pass
            except:   
                error_occured = True
            try:
                testopen = zipfile.ZipFile(local_fn + "_temp", 'r')
                try:
                    testopen.close()
                except:
                    pass
            except: 
                print("Cannot open downloaded file (%s)" % (local_fn + "_temp"))  
                error_occured = True
            
            if error_occured == False:  
                if os.path.exists(local_fn):
                    os.remove(local_fn)
                os.rename(local_fn + "_temp", local_fn )
                
                size_online_last_download = date_size_check_online
                
                self.FINAL_DOWNLOAD_LINKS[idx] = (url_, fn, time.time(), local_size, size_online_last_download
                                , date_size_check_online, size_online_latest) 
            
                error_occured = self._dump_bin_file(self.fn_final_download_list
                                    , self.FINAL_DOWNLOAD_LINKS) 
            else:
                print("Error occurred while downloading %s" % url_)
          
        print("Done!")
        return 
       
if __name__ == "__main__":
    
    
    pass
