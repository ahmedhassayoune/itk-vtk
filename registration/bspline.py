import itk
from utils import *

# https://itk.org/Doxygen/html/classitk_1_1BSplineTransform.html
# https://itk.org/Doxygen/html/Examples_2RegistrationITKv4_2DeformableRegistration7_8cxx-example.html
def reg_bspline(fixed_image, moving_image):
    TransformType = itk.BSplineTransform[itk.D, 3, 3]
    OptimizerType = itk.LBFGSBOptimizerv4
    MetricType = itk.MeanSquaresImageToImageMetricv4[InputImageType, InputImageType]
    RegistrationType = itk.ImageRegistrationMethodv4[InputImageType, InputImageType]

    metric = MetricType.New()
    optimizer = OptimizerType.New()
    registration = RegistrationType.New()

    registration.SetMetric(metric)
    registration.SetOptimizer(optimizer)

    registration.SetFixedImage(fixed_image)
    registration.SetMovingImage(moving_image)

    outputBSplineTransform = TransformType.New()

    InitializerType = itk.BSplineTransformInitializer[TransformType, InputImageType]

    transformInitializer = InitializerType.New()

    meshSize = [5, 5, 5]

    transformInitializer.SetTransform(outputBSplineTransform)
    transformInitializer.SetImage(fixed_image)
    transformInitializer.SetTransformDomainMeshSize(meshSize)
    transformInitializer.InitializeTransform()

    parameters = itk.OptimizerParameters[itk.D]([0.0] * outputBSplineTransform.GetNumberOfParameters())
    outputBSplineTransform.SetParameters(parameters)

    # One level registration process with shrinking factor 1 and smoothing sigma 0
    registration.SetInitialTransform(outputBSplineTransform)
    registration.InPlaceOn()

    registration.SetNumberOfLevels(1)
    registration.SetSmoothingSigmasPerLevel([0])
    registration.SetShrinkFactorsPerLevel([1])

    # the LBFGSB Optimizer does not support scales estimator and sets all the parameters scales to 1
    numParameters = outputBSplineTransform.GetNumberOfParameters()

    boundSelect = [0] * numParameters # UNBOUNDED https://itk.org/Doxygen/html/classitk_1_1LBFGSBOptimizerv4.html
    upperBound = [0.0] * numParameters
    lowerBound = [0.0] * numParameters

    optimizer.SetBoundSelection(boundSelect)
    optimizer.SetUpperBound(upperBound)
    optimizer.SetLowerBound(lowerBound)

    optimizer.SetCostFunctionConvergenceFactor(1e+12)
    optimizer.SetGradientConvergenceTolerance(1.0e-35)
    optimizer.SetNumberOfIterations(500)
    optimizer.SetMaximumNumberOfFunctionEvaluations(500)
    optimizer.SetMaximumNumberOfCorrections(5)

    registration.Update()

    finalParameters = outputBSplineTransform.GetParameters()
    numberOfIterations = optimizer.GetCurrentIteration()
    bestValue = optimizer.GetValue()

    # Display the result
    print('#########################################')
    print(f'  finalParameters    : {finalParameters}')
    print(f'  numberOfIterations : {numberOfIterations}')
    print(f'  bestValue          : {bestValue}')
    print('#########################################')

    # resample the moving image and save it
    ResampleFilterType = itk.ResampleImageFilter[InputImageType, InputImageType]
    resampler = ResampleFilterType.New()

    resampler.SetTransform(outputBSplineTransform)
    resampler.SetInput(moving_image)
    resampler.SetSize(fixed_image.GetLargestPossibleRegion().GetSize())
    resampler.SetOutputOrigin(fixed_image.GetOrigin())
    resampler.SetOutputSpacing(fixed_image.GetSpacing())
    resampler.SetOutputDirection(fixed_image.GetDirection())
    resampler.SetDefaultPixelValue(0)

    save_image(resampler.GetOutput(), 'Data/bspline_registered_gre2.nrrd')

    return resampler.GetOutput()
