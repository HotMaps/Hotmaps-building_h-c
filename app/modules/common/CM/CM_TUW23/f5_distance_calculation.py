import os
import sys
import numpy as np
from scipy.ndimage import binary_erosion
from scipy.spatial.distance import cdist
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)


def feature_dist(input_labels, struct=np.ones((3, 3))):
    """
    Takes a labeled array as returned by scipy.ndimage.label and
    returns an intra-feature distance matrix.

    The functions calculates the distance between every two non-zero element of
    the input matrix. In order to accelerate the calculation type and avoid
    unnecessary calculation, the inner pixels within the coherent regions
    should be removed. The inner pixels of coherent areas are obtained through
    binary erosion and set to zero.
    """
    # remove the pixels inside the coherent
    input_errosion = binary_erosion(input_labels, structure=struct)
    input_labels[input_errosion] = 0
    I, J = np.nonzero(input_labels)
    labels = input_labels[I, J]
    coords = np.column_stack((I, J))
    sorter = np.argsort(labels)
    labels = labels[sorter]
    coords = coords[sorter]
    I = I[sorter]
    J = J[sorter]
    sq_dists = cdist(coords, coords, 'sqeuclidean')
    start_idx = np.flatnonzero(np.r_[1, np.diff(labels)])
    nonzero_vs_feat = np.minimum.reduceat(sq_dists, start_idx, axis=1)
    feat_vs_feat = np.minimum.reduceat(nonzero_vs_feat, start_idx, axis=0)
    # calculate the distance between every two coherent areas
    # distance factor for one pixel to meter: 100
    distance_matrix = 100 * np.sqrt(feat_vs_feat)
    nRow, nCol = sq_dists.shape[0], start_idx.shape[0]
    # add the index of the final element to the slice array
    slice_indices = np.concatenate((start_idx, np.array([nRow])))
    col_args = np.zeros((nRow, nCol)).astype(int)
    row_index = np.zeros((nCol, nCol)).astype(int)
    '''
    How the following commands work:
        find closest pixel from label A to label B:
            Label A --> Label B
            row_index[A-1, B-1] = alpha
            col_index[A-1, B-1] = col_args[alpha, B-1] = beta
            index of pixel from Label A: input_labels[ I[alpha], J[alpha]]
            index of pixel from Label B: input_labels[ I[beta], J[beta]]
    '''
    for i in range(nCol):
        col_args[:, i] = start_idx[i] + \
                         np.argmin(sq_dists[:, slice_indices[i]:
                                            slice_indices[i+1]], axis=1)
    elements = sq_dists[np.arange(nRow).reshape((nRow, 1)), col_args]
    for i in range(nCol):
        row_index[i, :] = start_idx[i] + \
                           np.argmin(elements[slice_indices[i]:
                                              slice_indices[i+1], :], axis=0)
    col_index = col_args[row_index, np.arange(nCol).reshape((1, nCol))]
    # Change col_index and row_index to input array index.
    row_index_from_label = I[row_index]
    col_index_from_label = J[row_index]
    row_index_to_label = I[col_index]
    col_index_to_label = J[col_index]
    return distance_matrix, row_index_from_label, col_index_from_label, \
        row_index_to_label, col_index_to_label
