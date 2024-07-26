import itk
from utils import apply_smoothing

def seg_watershed(image, labels):
    image = apply_smoothing(image, method='gradient_anisotropic_diffusion')
    print("Image smoothed!")
    
    # Compute the gradient magnitude of the smoothed image
    gradient_magnitude = itk.GradientMagnitudeImageFilter.New(
        Input=image,
    )
    gradient_magnitude.Update()
    print("Gradient magnitude computed!")
    
    # Apply the watershed filter
    watershed = itk.WatershedImageFilter.New(
        Input=gradient_magnitude.GetOutput(),
        Threshold=0.01,
        Level=0.2
    )
    watershed.Update()
    watershed = watershed.GetOutput()
    print("Watershed segmentation completed!")
    
    # Extract connected components
    watershed_type = type(watershed)
    relabel_type = itk.Image[itk.SS, 3]
    relabel = itk.RelabelComponentImageFilter[watershed_type, relabel_type].New(
        Input=watershed,
        MinimumObjectSize=100
    )
    relabel.Update()
    labeled_image = relabel.GetOutput()
    print("Connected components relabeled!")
    
    # Get statistics of the connected components
    stats = itk.LabelStatisticsImageFilter[type(image), type(labeled_image)].New(
        Input=image,
        LabelInput=labeled_image
    )
    stats.Update()
    print("Connected components statistics computed!")
    
    # Extract the tumors using ThresholdImageFilter
    thresholds = []
    for label in labels:
        th = itk.BinaryThresholdImageFilter.New(
            Input=labeled_image,
            LowerThreshold=label,
            UpperThreshold=label,
            InsideValue=1,
            OutsideValue=0
        )
        th.Update()
        thresholds.append(th.GetOutput())
        
    combined = None
    for threshold in thresholds:
        if combined is None:
            combined = threshold
        else:
            combined = itk.OrImageFilter.New(
                Input1=combined,
                Input2=threshold
            )
            combined.Update()
            combined = combined.GetOutput()
        
    # Apply the binary mask to the original image
    mask = itk.MaskImageFilter.New(
        Input=image,
        MaskImage=combined
    )
    mask.Update()

    return mask.GetOutput()
    