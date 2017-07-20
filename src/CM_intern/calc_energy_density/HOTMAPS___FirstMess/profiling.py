import pstats
from numpy.lib import  savetxt
import os


#p = pstats.Stats('testoutput/' +'ee_lab152746')
#p1 = pstats.Stats('ee_lab1')
#path_ = "/media/SSD960GB/invert_eelab/invert_eelab_model/ee-lab/src"
#path_ = "/media/SSD960GB/invert_eelab/invert_eelab_model/ee-lab_test_no_svn/eelab_test_environment"
#path_ += "/eelab/main/testoutput/"
line_profiler("split.py.lprof")

path_ = ""
p2 = pstats.Stats('%ssplit.py.lprof' % path_)



#p3 = pstats.Stats('ee_lab4')
#p1 = pstats.Stats('ee_lab_1')
#p = pstats.Stats('ee_lab')
#p = pstats.Stats('ee_lab_find_me_now')

#p.strip_dirs().sort_stats(-1).print_stats()
#p.sort_stats('name').print_stats(5000)
#p.print_stats()
#p.sort_stats('cumulative').print_stats(10)
#p.sort_stats('cumulative').print_stats(50)
#p.sort_stats('cumulative').print_stats(50)
#p1.sort_stats('cumulative').print_stats(20)
#p = pstats.Stats('ee_lab143023')
#p.sort_stats('cumulative').print_stats(20)
#p1.sort_stats('time').print_stats(20)

p2.sort_stats('cumulative').print_stats(20)
p2.sort_stats('time').print_stats(200)
#p3.sort_stats('time').print_stats(20)