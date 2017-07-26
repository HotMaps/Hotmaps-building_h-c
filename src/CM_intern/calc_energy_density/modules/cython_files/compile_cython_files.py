# -*- coding: iso-8859-15 -*-
#"""
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from shutil import move, copyfile
import os,sys,shutil
import numpy

PYTHON_VERSION = sys.version_info[0]



"""
start with
# python compile_cython_files.py build_ext --inplace

cc1.exe error: unrecognized command line option -mno-cygwin

The -mno-cygwin option doesn't actually exist anymore in the newer versions of gcc.
But Windows Python 2.7's (I didn't try the others) distutils still tries to call it
anyway if you actually need something compiled. After actually way more Googling than I
probably should have needed, I finally stumbled upon this Stack Overflow answer.

Basically, you just need to edit [YourPythonInstallPath]\Lib\distutils\cygwinccompiler.py
and remove all traces of -mno-cygwin, and try again and it'll probably work fine.
Assuming you don't run into other errors (like say, actually trying to use 64-bit Python...).

"""

directory = ["cython_files"] #hdf5_auswertung_bcat_core_loop_step1"]#"heat_days"#/core/"agent_based"#export"#renovation"#"export_results"#"loop_adjust_number_of_dhw_stand_alone"
exclude_directories = ["compare_stable"]
#directory = "check_dhw_num_buildings/"
#exclude_directories = ["compare_stable"]


create_freeze = False
compile_even_if_exists = True

def compilecythonfiles():

    if (os.name == "posix"):
        #on linux machines compile all pyx files
        string_must_be_included = directory
        #string_must_be_included = "compute_ratio_change_core_function"
    else:
        string_must_be_included = directory

    CopyInputFiles(string_must_be_included, create_freeze)
    print("all .pyx files have been cythoned")

class CopyInputFiles():


    def __init__(self,directory
                 , create_freeze=False):
        print(sys.version_info)
        run_64bit_python = sys.maxsize > 2**32
        if run_64bit_python == True:
            fn_bit_info ="_64"
        else:
            fn_bit_info ="_32"

        curr_dir1 = sys.path[0]
        a = (((sys.path[0].rpartition("/"))[2]).rpartition("\\"))[-1]
        curr_dir = curr_dir1[0:-len(a)-1]
        curr_dir = curr_dir.replace("\\","/")
        #curr_dir = curr_dir[:-6]
        print(curr_dir)
        #curr_dir = curr_dir[:-6]
        print(curr_dir)
        if create_freeze == False:
            extensions = [".pyx"]
            curr_dir2move = curr_dir.rstrip("/") +"/"
        else:
            extensions = [".pyx",".py"]
            pos = (curr_dir.rstrip("/")).rfind("/")
            curr_dir2move = curr_dir[:pos] + "_freeze" + curr_dir[pos:] + "/"
            if os.path.isdir(curr_dir2move) == False:
                os.makedirs(curr_dir2move)
        file_dict = self.__dirEntries([curr_dir], True, {}, extensions)

        for key in file_dict:
            print (key + ": \n   " + str(file_dict[key]) + "\n")
        f = file_dict
        for key in file_dict:
            if (type(exclude_directories) is str or 
                    (PYTHON_VERSION == 2 and type(exclude_directories) is unicode)):
                if exclude_directories in key:
                    continue
            else:
                exclude_clause_fullfilled = True
                for jj in exclude_directories:
                    if jj in key:
                        exclude_clause_fullfilled = False
                        break
                if exclude_clause_fullfilled == False:
                    continue
                if os.path.isfile(key) == False:
                    print ('\n\n------->  %s    doesnt exist \n\n===================='%key)
                    continue

            curr_file_data = file_dict[key]
            curr_dir_file = key
            if (type(directory) is str or 
                    (PYTHON_VERSION == 2 and type(directory) is unicode)):
                if directory not in key:
                    continue
            elif type(directory) is list:
                criteria_fullfilled = True
                for jj in directory:
                    if jj not in key:
                        criteria_fullfilled = False
                        break
                if criteria_fullfilled == False:
                    continue
            print ('====================')
            if True:
                #might not needed as underline comes after .
                if (curr_file_data[2][-3:] + curr_file_data[3] == fn_bit_info + ".pyx"
                    and (curr_file_data[0]+curr_file_data[1]+curr_file_data[2][:-3]+curr_file_data[3] in file_dict)):
                    try:
                        os.remove(key)
                    except:
                        print ("############################\nError:\n%s exists already, failed deleting it"%key)
                    sys.exit()
                if curr_file_data[3] == ".pyx":
                    pyx_file_name2build = curr_file_data[2] + fn_bit_info
                elif curr_file_data[3] == ".py":
                    pyx_file_name2build = curr_file_data[2]

                pyx_dir2build = curr_file_data[0] + curr_file_data[1]

                pyx_file2build_no_ext = pyx_dir2build + pyx_file_name2build
                pyx_file2build = pyx_file2build_no_ext + ".pyx"
                if os.path.isfile(pyx_file2build) == True:
                    try:
                        os.remove(pyx_file2build)
                    except:
                        print ("############################\nError:\n%s exists already, failed deleting it" % pyx_file2build)
                        sys.exit()

                new_file_excl_ext = pyx_file_name2build

                print(new_file_excl_ext)

                src_folder =  curr_file_data[0] + curr_file_data[1]
                dest_folder = curr_dir2move + curr_file_data[1]
                if os.path.isdir(dest_folder) == False:
                    os.makedirs(dest_folder)

                print ('\n')
                if pyx_file_name2build == "__init__":
                    try:
                        if os.path.isfile(dest_folder+ pyx_file_name2build +'.py') == True:
                            try:
                                os.remove(dest_folder+ pyx_file_name2build +'.py')
                            except:
                                print('\n############################################\nCouldnt delete %s\n############################################\n'%(dest_folder+ pyx_file_name2build +'.py'))
                        shutil.copyfile(src_folder+ pyx_file_name2build +'.py', dest_folder + pyx_file_name2build + '.py')
                    except:
                        print('\n############################################\nCouldnt copy %s\n############################################\n'%( dest_folder + pyx_file_name2build + '.py'))
                elif os.path.isfile(dest_folder + pyx_file_name2build + ".pyd") == False or compile_even_if_exists == True:

                    copyfile(curr_dir_file, pyx_file2build)
                    osinfo=  os.name
                    for j in range(5):
                        if j==0:
                            ef = '.'+'c'
                        elif j==1 and osinfo =="posix":
                            ef = '.'+'so'
                        elif j==2:
                            ef = '.'+'o'
                        elif j==3:
                            ef = '.'+'def'
                        elif osinfo !="posix":
                            ef = '.'+'pyd'
                        try:
                            curr_file_in_src = src_folder + pyx_file_name2build + ef
                            curr_file_in_dest = dest_folder + pyx_file_name2build + ef
                            os.remove(curr_file_in_src)
                            os.remove(curr_file_in_dest)
                            print(curr_file_in_dest + ' deleted')

                        except:
                            pass
                    import numpy
                    try:

                        try:
                            if osinfo == "posix":
                                setup(
                                cmdclass = {'build_ext': build_ext},
                                ext_modules = [Extension(pyx_file_name2build, [pyx_file2build]
                                               , extra_compile_args=['-fopenmp', '-O3', '-ffast-math', '-march=native']
                                               , extra_link_args=['-fopenmp']
                                               , include_dirs=[numpy.get_include()])])
                            else:

                                setup(
                                cmdclass = {'build_ext': build_ext},
                                ext_modules = [Extension(pyx_file_name2build, [pyx_file2build],
                                                         include_dirs=[numpy.get_include()])])
                        except:
                            raise
                            print("include: numpy.get_include() ")
                            setup(
                            cmdclass = {'build_ext': build_ext},
                            ext_modules = [Extension(pyx_file_name2build, [pyx_file2build], include_dirs=[numpy.get_include()])])

                    except:
                        try:
                            os.remove(pyx_file2build)
                        except:
                            print("unable to delete: %s"%pyx_file2build)

                        raise("raise error")



                    for j in range(5):
                        if j==0:
                            ef = '.'+'c'
                        elif j==2:
                            ef = '.'+'o'
                        elif j==3:
                            ef = '.'+'def'
                        try:
                            curr_file_in_dest = src_folder + pyx_file_name2build + ef
                            os.remove(curr_file_in_dest)
                            print(curr_file_in_dest + ' deleted')
                        except:
                            pass


                    try:
                        os.remove(pyx_file2build)
                    except:
                        print("unable to delete: %s"%pyx_file2build)


                    if osinfo !="posix":
                        try:
                            move(curr_dir1 + "/" + pyx_file_name2build +'.pyd',
                                 dest_folder + pyx_file_name2build + '.pyd')
                        except:
                            print('\n############################################\nIF Windows used: .pyd not move - prev. .pvd file might be locked\n############################################\n')
                    else:
                        try:
                            move(curr_dir1 + '/' + pyx_file_name2build + '.so',
                                 dest_folder + pyx_file_name2build + '.so')
                            print ('OK')
                        except:
                            print('\n############################################\nIF Linux/Unix used: .so not move - prev. .so file might be locked\n############################################\n')

        try:
            shutil.rmtree(curr_dir1+"/build")
            print('Build removed')
        except:
            pass
        print ('\n\n')



    def __dirEntries(self,dir_name, subdir, fileList = {}, extensions = None, *args):
        '''Return a list of file names found in directory 'dir_name'
        If 'subdir' is True, recursively access subdirectories under 'dir_name'.
        Additional arguments, if any, are file extensions to match filenames. Matched
            file names are added to the list.
        If there are no additional arguments, all files found in the directory are
            added to the list.
        Example usage: fileList = dirEntries(r'H:\TEMP', False, 'txt', 'py')
            Only files with 'txt' and 'py' extensions will be added to the list.
        Example usage: fileList = dirEntries(r'H:\TEMP', True)
            All files and all the files in subdirectories under H:\TEMP will be added
            to the list.
        '''
        base_folder = dir_name[0].rstrip("/")
        len_base_folder = len(base_folder)
        for curr_dir in dir_name:
            curr_sub_dir = (curr_dir)[len_base_folder+1:]
            if len(curr_sub_dir) > 0:
                curr_sub_dir += "/"
            for item in os.listdir(curr_dir):
                dirfile = os.path.join(curr_dir, item).replace("\\", "/")
                if (dirfile).find("kernprof") == -1:

                    if os.path.isfile(dirfile):
                        file_name = dirfile[len(os.path.dirname(dirfile))+1:]
                        append_file = False
                        if file_name.count(".") != 1:
                            pass
                        elif not extensions:
                            append_file = True
                        else:
                            for element in extensions:
                                if file_name[-len(element):] == element:
                                    append_file = True
                                    break
                        if  append_file == True:
                            file_ext = "." + (file_name.rpartition("."))[-1]
                            fileList[dirfile] = (base_folder +"/", curr_sub_dir,file_name[:-(len(file_ext))], file_ext)


                    elif (os.path.isdir(dirfile) and subdir
                          and (dirfile).find(".svn") == -1
                          and dirfile.find("/test") == -1 and (dirfile).find(".") == -1
                          and (dirfile).find("IPython") == -1 and (dirfile != "tcl")
                          and (dirfile != "mpl-data")) :

                        pass
                        dir_name.append(dirfile.replace("\\","/"))


        return fileList




#"""
if __name__ == "__main__":
    compilecythonfiles()
    #CopyInputFiles(directory)
    #print "all .pyx files have been cythoned"
