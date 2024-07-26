import itk

gre1_filepath = 'Data/case6_gre1.nrrd'
gre2_filepath = 'Data/case6_gre2.nrrd'

InputImageType = itk.Image[itk.F, 3]
OutputImageType = itk.Image[itk.US, 3]

reader = itk.ImageFileReader[InputImageType].New()
reader.SetFileName(gre1_filepath)
reader.Update()
gre1_image = reader.GetOutput()

reader = itk.ImageFileReader[InputImageType].New()
reader.SetFileName(gre2_filepath)
reader.Update()
gre2_image = reader.GetOutput()

def save_image(image, output_filepath='output.nrrd'):
    if type(image) == InputImageType:
        caster = itk.CastImageFilter[InputImageType, OutputImageType].New(
            Input=image
        )
        writer = itk.ImageFileWriter[OutputImageType].New()
        writer.SetFileName(output_filepath)
        writer.SetInput(caster.GetOutput())
        writer.Update()
    else:
        writer = itk.ImageFileWriter[type(image)].New()
        writer.SetFileName(output_filepath)
        writer.SetInput(image)
        writer.Update()

# ----------------------------------------
# Smoothing methods
# ----------------------------------------
def gradient_anisotropic_diffusion(image, iterations=20, time_step=0.04, conductance=3):
    smoother = itk.GradientAnisotropicDiffusionImageFilter.New(
        Input=image,
        NumberOfIterations=iterations,
        TimeStep=time_step,
        ConductanceParameter=conductance
    )
    smoother.Update()
    return smoother.GetOutput()

def median(image, radius=2):
    smoother = itk.MedianImageFilter.New(
        Input=image,
        Radius=radius
    )
    smoother.Update()
    return smoother.GetOutput()

def gaussian(image, sigma=1.0):
    smoother = itk.SmoothingRecursiveGaussianImageFilter.New(
        Input=image,
        Sigma=sigma
    )
    smoother.Update()
    return smoother.GetOutput()

def curvilinear(image, iterations=5, alpha=0.5, beta=0.5):
    smoother = itk.CurvilinearDiffusionImageFilter.New(
        Input=image,
        NumberOfIterations=iterations,
        Alpha=alpha,
        Beta=beta
    )
    smoother.Update()
    return smoother.GetOutput()

def curvature_flow(image, iterations=10, time_step=0.0625):
    """Edge-preserving smoothing using curvature flow.

    Args:
        image (itk.Image): Input image
        iterations (int, optional): Number of iterations to run the filter. Defaults to 10.
        time_step (float, optional): Time step for the filter. Defaults to 0.0625.

    Returns:
        itk.Image: Smoothed image
    """
    smoother = itk.CurvatureFlowImageFilter.New(
        Input=image,
        NumberOfIterations=iterations,
        TimeStep=time_step
    )
    smoother.Update()
    return smoother.GetOutput()


def apply_smoothing(image, method='gradient_anisotropic_diffusion', **kwargs):
    smoothing_methods = {
        'gradient_anisotropic_diffusion': gradient_anisotropic_diffusion,
        'median': median,
        'gaussian': gaussian,
        'curvilinear': curvilinear,
        'curvature_flow': curvature_flow
    }
    if method in smoothing_methods:
        return smoothing_methods[method](image, **kwargs)
    else:
        raise ValueError(f"Unknown smoothing method: {method}")
