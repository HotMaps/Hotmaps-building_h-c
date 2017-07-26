# -*- coding: utf-8 -*-
"""
Created on July 26 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import time
'''
This modules is for calculating the indices of those pixels of a raster which
are covered with a vector. It considers an envelop around the vector layer and
returns min-xy and max-xy indices of the envelop within raster.
The indices are only for the overlapping part of a vector layer and a raster
'''


def calc_index(minx, maxy, dimX, dimY, fminx_, fmaxx_, fminy_, fmaxy_,
               resolution=100.0):
    '''
    minx:          minx Raster
    maxy:          maxy Raster
    dimX:          Raster X dimension
    dimY:          Raster Y dimension
    fminx_:        minx shapefile
    fmaxx_:        maxx shapefile
    fminy_:        miny shapefile
    fmaxy_:        maxy shapefile
    resolution:    Raster resolution
    '''
    fminx = fminy = 10**10
    fmaxx = fmaxy = 0
    # Get boundaries
    fminx = min(fminx_, fminx)
    fminy = min(fminy_, fminy)
    fmaxx = max(fmaxx_, fmaxx)
    fmaxy = max(fmaxy_, fmaxy)
    # define exact index that encompasses the feature.
    lowIndexY = int((fminx-minx)/resolution)
    lowIndexX = int((maxy-fmaxy)/resolution)
    upIndexY = lowIndexY + int((fmaxx-fminx)/resolution)
    upIndexX = lowIndexX + int((fmaxy-fminy)/resolution)
    while (minx + upIndexY*resolution) < fmaxx:
        upIndexY = upIndexY + 1
    while (maxy - upIndexX*resolution) > fminy:
        upIndexX = upIndexX + 1
    # check if input shapefile exceed the boundaries of input raster file.
    if lowIndexY < 0:
        lowIndexY = 0
    if lowIndexX < 0:
        lowIndexX = 0
    if upIndexY > dimY:
        upIndexY = dimY
    if upIndexX > dimX:
        upIndexX = dimX
    return (lowIndexX, upIndexX, lowIndexY, upIndexY)


if __name__ == "__main__":
    start = time.time()
    minx = 4285400
    maxy = 2890500
    dimX = 2953
    dimY = 5692
    fminx_ = 4285406.36383
    fmaxx_ = 4854633.29352
    fminy_ = 2595156.89558
    fmaxy_ = 2890412.7091390
    resolution = 100
    output = calc_index(minx, maxy, dimX, dimY, fminx_, fmaxx_, fminy_, fmaxy_)
    print('lowIndexX = %d \nupIndexX = %d \nlowIndexY = %d \nupIndexY = %d'
          % (output[0], output[1], output[2], output[3]))
    elapsed = time.time() - start
    print("%0.3f seconds" % elapsed)
