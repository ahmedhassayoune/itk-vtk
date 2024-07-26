import itk
from utils import *

COORD_SMALL_TUMOR = [98, 79, 83]
COORD_BIG_TUMOR = [86, 66, 51]
COORD_LAST_TUMOR = [123, 66, 82]

# https://itk.org/Doxygen/html/Examples_2Segmentation_2ThresholdSegmentationLevelSetImageFilter_8cxx-example.html
def seg_threshold_levelset(image, output_file):
    ThresholdingFilterType = itk.BinaryThresholdImageFilter[InputImageType, OutputImageType]
    thresholder = ThresholdingFilterType.New()
    thresholder.SetLowerThreshold(-4.0)
    thresholder.SetUpperThreshold(0.0)
    thresholder.SetOutsideValue(0)
    thresholder.SetInsideValue(255)

    FastMarchingFilterType = itk.FastMarchingImageFilter[InputImageType, InputImageType]
    fastMarching = FastMarchingFilterType.New()

    ThresholdSegmentationLevelSetImageFilterType = itk.ThresholdSegmentationLevelSetImageFilter[InputImageType, InputImageType, itk.F]
    thresholdSegmentation = ThresholdSegmentationLevelSetImageFilterType.New()
    thresholdSegmentation.SetPropagationScaling(1.0)
    thresholdSegmentation.SetMaximumRMSError(0.02)
    thresholdSegmentation.SetNumberOfIterations(1500)
    thresholdSegmentation.SetUpperThreshold(1000.0)
    thresholdSegmentation.SetLowerThreshold(400.0)
    thresholdSegmentation.SetIsoSurfaceValue(0.0)
    thresholdSegmentation.SetInput(fastMarching.GetOutput())
    thresholdSegmentation.SetFeatureImage(image)

    thresholder.SetInput(thresholdSegmentation.GetOutput())

    NodeContainer = itk.VectorContainer[itk.UI, itk.LevelSetNode[itk.F, 3]]
    NodeType = itk.LevelSetNode[itk.F, 3]

    seeds = NodeContainer.New()

    node_small_tumor = NodeType()
    node_small_tumor.SetValue(-1.7)
    node_small_tumor.SetIndex(COORD_SMALL_TUMOR)

    node_big_tumor = NodeType()
    node_big_tumor.SetValue(-4.6)
    node_big_tumor.SetIndex(COORD_BIG_TUMOR)

    node_last_tumor = NodeType()
    node_last_tumor.SetValue(-3.2)
    node_last_tumor.SetIndex(COORD_LAST_TUMOR)

    seeds.Initialize()
    seeds.InsertElement(0, node_small_tumor)
    seeds.InsertElement(1, node_big_tumor)
    seeds.InsertElement(2, node_last_tumor)

    fastMarching.SetTrialPoints(seeds)
    fastMarching.SetSpeedConstant(1.0)
    fastMarching.SetOutputRegion(image.GetBufferedRegion())
    fastMarching.SetOutputSpacing(image.GetSpacing())
    fastMarching.SetOutputOrigin(image.GetOrigin())
    fastMarching.SetOutputDirection(image.GetDirection())

    writer = itk.ImageFileWriter[OutputImageType].New()
    writer.SetFileName(output_file)
    writer.SetInput(thresholder.GetOutput())
    writer.Update()

    return thresholder.GetOutput()