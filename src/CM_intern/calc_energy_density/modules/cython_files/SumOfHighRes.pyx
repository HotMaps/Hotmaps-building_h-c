'''
Created on Apr 20, 2017

@author: simulant
'''
import time
import numpy as np

cimport numpy as np
from cython.parallel import parallel, prange

DTYPE1 = np.int
ctypedef np.int_t DTYPE1_t

DTYPE2 = np.float32
ctypedef np.float32_t DTYPE2_t

cimport cython

import os
 

def convert_vector(vector,type):
    try:
        if vector.dtype == type:
            pass
            return vector
        if vector.ndim == 1:
            vector1 = np.zeros(vector.shape[0],dtype=type)
            vector1[:] = vector
        else:
            vector1 = np.zeros(vector.shape,dtype=type)
            vector1[:,:] = vector
    except:
        vector1 = type(vector)
    return(vector1)

def CalcAverageBased(HighResM,
                     ResolutionFactor,
                     NumberOfLoops,
                     WeightFaktor):
    
    HighResM = convert_vector(HighResM, DTYPE2)
    ResolutionFactor = convert_vector(ResolutionFactor, DTYPE1)
    NumberOfLoops = convert_vector(NumberOfLoops, DTYPE1)
    WeightFaktor = convert_vector(WeightFaktor, DTYPE2)
    st = time.time()
    
    HighResM = CoreLoopCalcAverageBased(HighResM,
                     ResolutionFactor,
                     NumberOfLoops,
                     WeightFaktor)
    
    print(time.time() - st)   
    return HighResM

@cython.wraparound(False)
@cython.boundscheck(False) 
@cython.cdivision(True) 
def CoreLoopCalcAverageBased(np.ndarray[DTYPE2_t, ndim=2] HighResM,
                     DTYPE1_t ResolutionFactor,
                     DTYPE1_t NumberOfLoops,
                     DTYPE2_t WeightFaktor):
    
 
    cdef DTYPE1_t i
    cdef DTYPE1_t r
    cdef DTYPE1_t c
    cdef DTYPE1_t r_
    cdef DTYPE1_t c_
    cdef DTYPE2_t correction_factor
    cdef DTYPE2_t WeightFaktor2
    cdef DTYPE2_t TEMP_Val
    cdef DTYPE2_t TEMP_Val2
    
    cdef DTYPE1_t rLow
    cdef DTYPE1_t cLow
    
    cdef DTYPE1_t rH2
    cdef DTYPE1_t cH2
    cdef DTYPE1_t rHighBase
    cdef DTYPE1_t cHighBase
    cdef DTYPE1_t rHigh
    cdef DTYPE1_t cHigh    
    cdef DTYPE2_t change_factor_
    
    
    r = HighResM.shape[0]
    c = HighResM.shape[1]
    
    rLow = r / ResolutionFactor
    cLow = c / ResolutionFactor
    
    #cdef np.ndarray[DTYPE2_t, ndim=2] change_factor = np.zeros((r/ResolutionFactor, c/ResolutionFactor), dtype= DTYPE2)
    cdef np.ndarray[DTYPE2_t, ndim=2] LowResSumOrig = np.zeros((r/ResolutionFactor, c/ResolutionFactor), dtype= DTYPE2)
    cdef np.ndarray[DTYPE2_t, ndim=2] LowResSumNew = np.zeros((r/ResolutionFactor, c/ResolutionFactor), dtype= DTYPE2)

    
    cdef np.ndarray[DTYPE2_t, ndim=2] HighResM_new = np.zeros((r, c), dtype= DTYPE2)
    cdef np.ndarray[DTYPE1_t, ndim=2] idxM_x_res = np.zeros((r, c), dtype= DTYPE1)
    cdef np.ndarray[DTYPE1_t, ndim=2] idxM_y_res = np.zeros((r, c), dtype= DTYPE1)
    
    
    st = time.time()
    
    LowResSumOrig[:, :] = CoreLoopSumLowRes(HighResM, 
                        ResolutionFactor)
    print ("   SumLowRes: %4.2f sec" %(time.time() - st))

    
    correction_factor = 1 + 4 * WeightFaktor * (1 + 1/ 1.41)
    WeightFaktor /= correction_factor
    WeightFaktor2 = WeightFaktor / 1.41

    
    print ("CoreLoopCalcAverageBased: Run %i Loops" % NumberOfLoops)
    for i in range(NumberOfLoops):
        st = time.time()
        for r_ in range(r):
            HighResM_new[r_, 0] = HighResM[r_, 0]
            HighResM_new[r_, c-1] = HighResM[r_, c-1]
        for c_ in range(c):
            HighResM_new[0, c_] = HighResM[0, c_]
            HighResM_new[r-1, c_] = HighResM[r-1, c_]
        for r_ in range(1, r-1):
            for c_ in range(1, c-1):
                
                TEMP_Val = HighResM[r_+1,c_]
                TEMP_Val += HighResM[r_-1,c_]
                TEMP_Val += HighResM[r_,c_+1]
                TEMP_Val += HighResM[r_,c_-1]
                TEMP_Val *= WeightFaktor
                
                TEMP_Val += HighResM[r_,c_] / correction_factor
                

                TEMP_Val2 = HighResM[r_-1,c_-1]
                TEMP_Val2 += HighResM[r_+1,c_+1]
                TEMP_Val2 += HighResM[r_-1,c_+1]
                TEMP_Val2 += HighResM[r_+1,c_-1]
                TEMP_Val2 *= WeightFaktor2
                
                
                HighResM_new[r_,c_] = TEMP_Val  + TEMP_Val2

        
           
        LowResSumNew[:, :] = CoreLoopSumLowRes(HighResM_new, 
                        ResolutionFactor)
        #with nogil, parallel():
        if 1==1:
            for r_ in range(rLow):
                rHighBase = r_ * ResolutionFactor
                for c_ in range(cLow):
                    cHighBase = c_ * ResolutionFactor
                    change_factor_ = (0.01 + LowResSumOrig[r_, c_]) / (0.01 + LowResSumNew[r_, c_])

    
                    for rH2 in range(ResolutionFactor):
                        rHigh = rHighBase + rH2
                        for cH2 in range(ResolutionFactor):
                            cHigh = cHighBase + cH2

                            HighResM[rHigh, cHigh] = HighResM_new[rHigh, cHigh] * change_factor_
                            """except:
                                pass
                                
                                print(LowResM.shape[0])
                                print(LowResM.shape[1])
                                print(HighResM.shape[0])
                                print(HighResM.shape[1])
                                print "....."
                                print(rLow)
                                print(cLow)
                                print(rHigh)
                                print(cHigh)
                                print "....."
                                print LowResM[rLow, cLow]
                                print HighResM[rHigh, cHigh]
                            """
        #HighResM[:,:] = HighResM_new
        print ("   LoopTime: %4.2f sec" %(time.time() - st))

        

    return HighResM
     
        
         

def CalcSum(HighResM,
            ResolutionFactor):
    
    
    HighResM = convert_vector(HighResM, DTYPE2)
    ResolutionFactor = convert_vector(ResolutionFactor, DTYPE1)
    
    

    (LowResSum) = CoreLoopSumLowRes(HighResM, 
                        ResolutionFactor)

    return (LowResSum )                    
"""
@cython.wraparound(False)
@cython.boundscheck(False)                             
"""   
#def CoreLoopSumLowRes(HighResM,
#               ResolutionFactor):
@cython.wraparound(False)
@cython.boundscheck(False)  
def CoreLoopSumLowRes(np.ndarray[DTYPE2_t, ndim=2] HighResM,
               DTYPE1_t ResolutionFactor):  
    
    cdef DTYPE1_t rL
    cdef DTYPE1_t cL
    cdef DTYPE1_t rLow
    cdef DTYPE1_t cLow

    
    cdef DTYPE1_t rH2
    cdef DTYPE1_t cH2
    cdef DTYPE1_t r
    cdef DTYPE1_t c
    
    r = HighResM.shape[0]
    c = HighResM.shape[1]
    
    rLow = np.ceil(r/ ResolutionFactor)
    cLow = np.ceil(c/ ResolutionFactor)
    #LowResSum = np.zeros((np.ceil(r/ ResolutionFactor), np.ceil(c/ ResolutionFactor)), dtype= DTYPE2)
    cdef np.ndarray[DTYPE2_t, ndim=2] LowResSum = np.zeros((rLow, cLow), dtype= DTYPE2)
   
    with nogil, parallel():
        #if 1==1:
        for rL in prange(rLow):
            #rHighBase = rL * ResolutionFactor
            for cL in range(cLow):
                #cHighBase = cL * ResolutionFactor
                for rH2 in range(ResolutionFactor):
                    #rHigh = rL * ResolutionFactor + rH2
                    for cH2 in range(ResolutionFactor):
                        #cHigh = cL * ResolutionFactor + cH2
                        
                        LowResSum[rL, cL] += HighResM[rL * ResolutionFactor + rH2, cL * ResolutionFactor + cH2]      
                        #LowResSum[rL, cL] += HighResM[rHigh, cHigh]                   
                        
    return LowResSum


def CalcHighRes(LowResM,
            ResolutionFactor):
    
    
    LowResM = convert_vector(LowResM, DTYPE2)
    ResolutionFactor = convert_vector(ResolutionFactor, DTYPE1)

    (HighResM) = CoreLoopHighRes(LowResM, 
                        ResolutionFactor)

    return (HighResM ) 


@cython.wraparound(False)
@cython.boundscheck(False)  
def CoreLoopHighRes(np.ndarray[DTYPE2_t, ndim=2] LowResM,
               DTYPE1_t ResolutionFactor):  
    
    cdef DTYPE1_t rL
    cdef DTYPE1_t cL
    cdef DTYPE1_t rLow
    cdef DTYPE1_t cLow

    
    cdef DTYPE1_t rH2
    cdef DTYPE1_t cH2
    cdef DTYPE1_t rHighBase
    cdef DTYPE1_t cHighBase
    cdef DTYPE1_t rHigh
    cdef DTYPE1_t cHigh
    cdef DTYPE1_t r
    cdef DTYPE1_t c
    
    rLow = LowResM.shape[0]
    cLow = LowResM.shape[1]
    
    r = rLow * ResolutionFactor
    c = cLow * ResolutionFactor
    
    
    cdef np.ndarray[DTYPE2_t, ndim=2] HighResM = np.zeros((r, c), dtype= DTYPE2)
    
    if 1== 1:
        for rL in range(rLow):
            rHighBase = rL * ResolutionFactor
            for cL in range(cLow):
                cHighBase = cL * ResolutionFactor
                for rH2 in range(ResolutionFactor):
                    rHigh = rHighBase + rH2
                    for cH2 in range(ResolutionFactor):
                        cHigh = cHighBase + cH2

                        #try:
                        HighResM[rHigh, cHigh] = LowResM[rL, cL]
                        """
                        except:
                            print(LowResM.shape[0])
                            print(LowResM.shape[1])
                            print(HighResM.shape[0])
                            print(HighResM.shape[1])
                            print "....."
                            print(rLow)
                            print(cLow)
                            print(rHigh)
                            print(cHigh)
                            print "....."
                            print LowResM[rLow, cLow]
                            print HighResM[rHigh, cHigh]
                        """
                        
    return HighResM  
        
        