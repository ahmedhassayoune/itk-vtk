import itk
from utils import apply_smoothing


def seg_connected_threshold(image, lower, upper, seedX, seedY, seedZ):
    image = apply_smoothing(image, method='gradient_anisotropic_diffusion')
    connected_threshold = itk.ConnectedThresholdImageFilter.New(
        Input=image,
        ReplaceValue=255,
        Lower=lower,
        Upper=upper,
        Seed=(seedX, seedY, seedZ)
    )
    connected_threshold.Update()
    return connected_threshold.GetOutput()
