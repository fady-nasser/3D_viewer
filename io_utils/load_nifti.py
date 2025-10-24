import nibabel as nib
import numpy as np

def load_nifti(path):
    img = nib.load(path)
    data = img.get_fdata()
    return data

def save_nifti(data, path, affine=None):
    """Save data to a NIFTI file.
    
    Args:
        data: numpy array to save
        path: string path where to save the NIFTI file
        affine: optional 4x4 affine transformation matrix
    """
    if affine is None:
        affine = np.eye(4)
    img = nib.Nifti1Image(data, affine)
    nib.save(img, path)