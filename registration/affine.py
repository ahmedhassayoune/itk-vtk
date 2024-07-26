import itk
from utils import *

# https://itk.org/Doxygen/html/classitk_1_1AffineTransform.html
# https://itk.org/Doxygen/html/Examples_2RegistrationITKv4_2ImageRegistration20_8cxx-example.html
def reg_affine(fixed_image, moving_image):
    TransformType = itk.AffineTransform[itk.D, 3]
    OptimizerType = itk.RegularStepGradientDescentOptimizer
    MetricType = itk.MeanSquaresImageToImageMetric[InputImageType, InputImageType]
    InterpolatorType = itk.LinearInterpolateImageFunction[InputImageType, itk.D]
    RegistrationType = itk.ImageRegistrationMethod[InputImageType, InputImageType]

    metric = MetricType.New()
    optimizer = OptimizerType.New()
    interpolator = InterpolatorType.New()
    registration = RegistrationType.New()

    registration.SetMetric(metric)
    registration.SetOptimizer(optimizer)
    registration.SetInterpolator(interpolator)

    transform = TransformType.New()
    initial_parameters = itk.OptimizerParameters[itk.D]([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    transform.SetParameters(initial_parameters)
    registration.SetTransform(transform)

    registration.SetFixedImage(fixed_image)
    registration.SetMovingImage(moving_image)
    registration.SetFixedImageRegion(fixed_image.GetBufferedRegion())

    registration.SetInitialTransformParameters(transform.GetParameters())

    translationScale = 1.0 / 1000.0
    # the first 9 parameters correspond to the rotation matrix factors
    # the last 3 parameters are the translations applied after the multiplication with the rotation matrix
    optimizerScales = itk.OptimizerParameters[itk.D]([
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        translationScale,
        translationScale,
        translationScale
    ])
    optimizer.SetScales(optimizerScales)

    optimizer.SetMaximumStepLength(0.07)
    optimizer.SetMinimumStepLength(0.0001)
    optimizer.SetNumberOfIterations(2000)

    optimizer.MinimizeOn()

    registration.Update()

    finalParameters = registration.GetLastTransformParameters()

    m00 = finalParameters[0]
    m01 = finalParameters[1]
    m02 = finalParameters[2]
    m10 = finalParameters[3]
    m11 = finalParameters[4]
    m12 = finalParameters[5]
    m20 = finalParameters[6]
    m21 = finalParameters[7]
    m22 = finalParameters[8]

    finalTranslationX = finalParameters[9]
    finalTranslationY= finalParameters[10]
    finalTranslationZ = finalParameters[11]
    numberOfIterations = optimizer.GetCurrentIteration()
    bestValue = optimizer.GetValue()

    # Display the result
    print('#########################################')
    print('  Rotation matrix')
    print(f'     {m00}       {m01}    {m02}')
    print(f'     {m10}      {m11}     {m12}')
    print(f'     {m20}   {m21}   {m22}')
    print(f'  finalTranslationX  : {finalTranslationX}')
    print(f'  finalTranslationY  : {finalTranslationX}')
    print(f'  finalTranslationZ  : {finalTranslationX}')
    print(f'  numberOfIterations : {numberOfIterations}')
    print(f'  bestValue          : {bestValue}')
    print('#########################################')

    # resample the moving image and save it
    finalTransform = TransformType.New()
    finalTransform.SetParameters(finalParameters)
    finalTransform.SetFixedParameters(transform.GetFixedParameters())

    ResampleFilterType = itk.ResampleImageFilter[InputImageType, InputImageType]
    resampler = ResampleFilterType.New()

    resampler.SetTransform(finalTransform)
    resampler.SetInput(moving_image)
    resampler.SetSize(fixed_image.GetLargestPossibleRegion().GetSize())
    resampler.SetOutputOrigin(fixed_image.GetOrigin())
    resampler.SetOutputSpacing(fixed_image.GetSpacing())
    resampler.SetOutputDirection(fixed_image.GetDirection())
    resampler.SetDefaultPixelValue(0)

    save_image(resampler.GetOutput(), 'Data/affine_registered_gre2.nrrd')

    return resampler.GetOutput()
