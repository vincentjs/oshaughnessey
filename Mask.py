import numpy as np

def fixit(A, mask, value):
    "Fix the list A by replacing items marked by mask with val"

    # Cast A as a numpy array
    B = np.array(A)
    # Assign masked elements with value
    B[mask] = value
    # Recast back to list
    A = np.ndarray.tolist(B)

    return A
