import itk
from utils import *

# https://itk.org/Doxygen/html/classitk_1_1VersorRigid3DTransform.html
# https://itk.org/Doxygen/html/Examples_2RegistrationITKv4_2ImageRegistration8_8cxx-example.html
def reg_rigid3D(fixed_image, moving_image):
    TransformType = itk.VersorRigid3DTransform[itk.D]
    OptimizerType = itk.RegularStepGradientDescentOptimizerv4[itk.D]
    MetricType = itk.MeanSquaresImageToImageMetricv4[InputImageType, InputImageType]
    RegistrationType = itk.ImageRegistrationMethodv4[InputImageType, InputImageType]

    metric = MetricType.New()
    optimizer = OptimizerType.New()
    registration = RegistrationType.New()

    registration.SetMetric(metric)
    registration.SetOptimizer(optimizer)

    initialTransform = TransformType.New()

    registration.SetFixedImage(fixed_image)
    registration.SetMovingImage(moving_image)

    # Align the center of the two volumes
    TransformInitializerType = itk.CenteredTransformInitializer[TransformType, InputImageType, InputImageType]
    initializer = TransformInitializerType.New()

    initializer.SetTransform(initialTransform)
    initializer.SetFixedImage(fixed_image)
    initializer.SetMovingImage(moving_image)

    # Use the center of mass
    initializer.MomentsOn()

    # Compute the center and translation and pass them to the transform
    initializer.InitializeTransform()

    # Rotation part of the transform initialized using a Versor (unit quaternion)
    # The Versor defines the type of the vector used to indicate the rotation axis
    VersorType = itk.Versor[itk.D]
    VectorType = itk.Vector[itk.D, 3]
    rotation = VersorType()
    axis = VectorType()
    axis[0] = 1.0
    axis[1] = 1.0
    axis[2] = 1.0
    angle = 0
    rotation.Set(axis, angle)
    initialTransform.SetRotation(rotation)

    registration.SetInitialTransform(initialTransform)

    translationScale = 1.0 / 1000.0
    optimizerScales = itk.OptimizerParameters[itk.D]([1.0, 1.0, 1.0, translationScale, translationScale, translationScale])

    optimizer.SetScales(optimizerScales)
    optimizer.SetNumberOfIterations(200)
    optimizer.SetLearningRate(0.2)
    optimizer.SetMinimumStepLength(0.001)
    optimizer.SetReturnBestParametersAndValue(True)

    # One level registration process without shrinking and smoothing
    numberOfLevels = 1

    shrinkFactorPerLevel = [1]
    smoothingSigmasPerLevel = [0]

    registration.SetNumberOfLevels(numberOfLevels)
    registration.SetSmoothingSigmasPerLevel(smoothingSigmasPerLevel)
    registration.SetShrinkFactorsPerLevel(shrinkFactorPerLevel)

    registration.Update()

    finalParameters = registration.GetOutput().Get().GetParameters()

    versorX = finalParameters[0]
    versorY = finalParameters[1]
    versorZ = finalParameters[2]
    finalTranslationX = finalParameters[3]
    finalTranslationY = finalParameters[4]
    finalTranslationZ = finalParameters[5]
    numberOfIterations = optimizer.GetCurrentIteration()
    bestValue = optimizer.GetValue()

    # Display the result
    print('#########################################')
    print(f'  versorX            : {versorX}')
    print(f'  versorY            : {versorY}')
    print(f'  versorZ            : {versorZ}')
    print(f'  finalTranslationX  : {finalTranslationX}')
    print(f'  finalTranslationY  : {finalTranslationY}')
    print(f'  finalTranslationZ  : {finalTranslationZ}')
    print(f'  numberOfIterations : {numberOfIterations}')
    print(f'  bestValue          : {bestValue}')
    print('#########################################')

    # resample the moving image and save it
    finalTransform = TransformType.New()
    finalTransform.SetFixedParameters(registration.GetOutput().Get().GetFixedParameters())
    finalTransform.SetParameters(finalParameters)

    matrix = finalTransform.GetMatrix()
    offset = finalTransform.GetOffset()

    print('Matrix : ')
    print(matrix)
    print('Offset : ')
    print(offset)

    ResampleFilterType = itk.ResampleImageFilter[InputImageType, InputImageType]
    resampler = ResampleFilterType.New()

    resampler.SetTransform(finalTransform)
    resampler.SetInput(moving_image)
    resampler.SetSize(fixed_image.GetLargestPossibleRegion().GetSize())
    resampler.SetOutputOrigin(fixed_image.GetOrigin())
    resampler.SetOutputSpacing(fixed_image.GetSpacing())
    resampler.SetOutputDirection(fixed_image.GetDirection())
    resampler.SetDefaultPixelValue(0)

    save_image(resampler.GetOutput(), 'Data/rigid3D_registered_gre2.nrrd')

    return resampler.GetOutput()
