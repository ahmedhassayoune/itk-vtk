from visualization import visualize
from registration.bspline import reg_bspline
from segmentation.threshold_levelset import seg_threshold_levelset
from utils import *
import os

if __name__ == "__main__":
    # Registration
    reg_path = "Data/bspline_registered_gre2.nrrd"
    if (os.path.exists(reg_path)):
        reader = itk.ImageFileReader[InputImageType].New()
        reader.SetFileName(reg_path)
        reader.Update()
        reg_gre2 = reader.GetOutput()
    else:
        reg_gre2 = reg_bspline(gre1_image, gre2_image)

    # Segmentation
    seg1_path = "Data/seg_threshold_levelset_gre1.nrrd"
    seg2_path = "Data/seg_threshold_levelset_registered_gre2.nrrd"

    if (os.path.exists(seg1_path) and os.path.exists(seg2_path)):
        # Load segmentation gre1
        reader = itk.ImageFileReader[OutputImageType].New()
        reader.SetFileName(seg1_path)
        reader.Update()
        seg_gre1 = reader.GetOutput()

        # Load segmentation gre2
        reader = itk.ImageFileReader[OutputImageType].New()
        reader.SetFileName(seg2_path)
        reader.Update()
        seg_gre2 = reader.GetOutput()
    else:
        seg_gre1 = seg_threshold_levelset(gre1_image, seg1_path)
        seg_gre2 = seg_threshold_levelset(reg_gre2, seg2_path)

    # Visualization

    file_paths_slice = [gre1_filepath, reg_path, seg1_path, seg2_path]
    file_paths_mod = [seg1_path, seg2_path]

    visualize(file_paths_slice, file_paths_mod, seg_gre1, seg_gre2, gre1_image, reg_gre2)