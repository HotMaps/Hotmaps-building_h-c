'''
Created on Apr 20, 2017

@author: simulant
'''

import sys, os

path = os.path.join( os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__)))), 'common' )
if path not in sys.path:
    sys.path.append(path)


print ("SYSPATH")
print (sys.path)
