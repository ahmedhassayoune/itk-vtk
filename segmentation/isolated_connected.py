import itk
from utils import apply_smoothing

GRE1_LOWER = 395
GRE1_SEED1 = (125, 64, 79)
GRE1_SEED2 = (126, 55, 79)

GRE2_LOWER = 395
GRE2_SEED1 = (120, 77, 83)
GRE2_SEED2 = (154, 89, 83)

def seg_isolated_connected(image, lower, seed1, seed2):
    image = apply_smoothing(image=image, method='curvature_flow')
    isolated = itk.IsolatedConnectedImageFilter.New(
        Input=image,
        ReplaceValue=255,
        Lower=lower,
        Seed1=seed1,
        Seed2=seed2
    )
    isolated.Update()
    return isolated.GetOutput()
