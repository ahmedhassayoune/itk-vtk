import itk
from utils import apply_smoothing

GRE1_SEED1 = (125, 64, 79)
GRE1_SEED2 = (99, 79, 83)
GRE1_SEED3 = (87, 67, 51)

GRE2_SEED1 = (119, 81, 81)
GRE2_SEED2 = (98, 94, 81)
GRE2_SEED3 = (83, 68, 55)

'''
if __name__ == "__main__":
    print('Registration started')
    gre2_image_registered = reg_rigid3D(gre1_image, gre2_image)
    print('Registration finished\nSegmentation started')
    save_image(seg_confidence_connected(image=gre1_image, seed=GRE1_SEED1), 'seg_gre1_01.nrrd')
    save_image(seg_confidence_connected(image=gre1_image, seed=GRE1_SEED2, n_iterations=10), 'seg_gre1_02.nrrd')
    save_image(seg_confidence_connected(image=gre1_image, seed=GRE1_SEED3, n_iterations=6, multiplier=2.2), 'seg_gre1_03.nrrd')
    print('Segmentation started\nVisualization starting')
    save_image(seg_confidence_connected(image=gre2_image_registered, seed=GRE2_SEED1), 'seg_gre2_registered_01.nrrd')
    save_image(seg_confidence_connected(image=gre2_image_registered, seed=GRE2_SEED2, n_iterations=3, multiplier=2), 'seg_gre2_registered_02.nrrd')
    save_image(seg_confidence_connected(image=gre2_image_registered, seed=GRE2_SEED3, n_iterations=6, multiplier=2.2), 'seg_gre2_registered_03.nrrd')
    render(get_volumes_list(["seg_gre1_01.nrrd","seg_gre1_02.nrrd", "seg_gre1_03.nrrd",
                             "seg_gre2_registered_01.nrrd", "seg_gre2_registered_02.nrrd", "seg_gre2_registered_03.nrrd"
                             ]))
    print('Visualization closed')
'''

def seg_confidence_connected(image, seed, n_iterations=4, multiplier=2.5, neighborhood_radius=1):
    image = apply_smoothing(image=image, method='curvature_flow')
    
    input_type = itk.Image[itk.F, 3]
    output_type = itk.Image[itk.UC, 3]
    confidence = itk.ConfidenceConnectedImageFilter[input_type, output_type].New(
        Input=image,
        Seed=seed,
        NumberOfIterations=n_iterations,
        Multiplier=multiplier,
        InitialNeighborhoodRadius=neighborhood_radius,
        ReplaceValue=255,
    )
    confidence.Update()
    return confidence.GetOutput()
