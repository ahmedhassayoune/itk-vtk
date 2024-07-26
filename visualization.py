import vtk
import numpy as np

from render3d import get_volumes_list


interactors = []
windows = []
reslices = []
renderers = []
action = 0
interactorStyles = []


def init_windows(num_windows=3):
    global interactors, windows, reslices, interactorStyles

    for i in range(num_windows):
        window =vtk.vtkRenderWindow()
        interactor =  vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(window)
        
        if(i < 4):
            interactorStyle = vtk.vtkInteractorStyleImage()
            interactor.AddObserver("MouseMoveEvent", MouseMoveCallback)
            interactorStyle.AddObserver("LeftButtonPressEvent", ButtonCallback)
            interactorStyle.AddObserver("LeftButtonReleaseEvent", ButtonCallback)
            interactorStyle.AddObserver("KeyPressEvent", key_press_event)
            interactor.SetInteractorStyle(interactorStyle)
        else:
            interactor.AddObserver("KeyPressEvent", key_press_event)

        window.SetInteractor(interactor)
        windows.append(window)
        interactors.append(interactor)
        interactorStyles.append(interactorStyle)

def ButtonCallback(obj, event):
    global action
    if event == "LeftButtonPressEvent":
        action = 1
    else:
        action = 0

def key_press_event(obj, event):
    try:
        for window in windows:
            window.Finalize()
        exit(0)
    except:
        exit(0)


def MouseMoveCallback(obj, event):
    global action
    (max_X, max_Y) = obj.GetEventPosition()
    (max_lastX, max_lastY) = obj.GetLastEventPosition()
    if action == 1:
        deltaY = (max_Y - max_lastY) * 0.1
        deltaX = (max_X - max_lastX) * 0.1
        if (deltaY < 0 or deltaX < 0):
            delta = min(deltaX, deltaY)
        else:
            delta = max(deltaX, deltaY)
        for i,reslice in enumerate(reslices):
            reslice.Update()
            sliceSpacing = reslice.GetOutput().GetSpacing()[2]
            matrix = reslice.GetResliceAxes()

            # move the center point that we are slicing through
            center = matrix.MultiplyPoint((0, 0, sliceSpacing*-delta, 1))
            matrix.SetElement(0, 3, center[0])
            matrix.SetElement(1, 3, center[1])
            matrix.SetElement(2, 3, center[2])
            reslice.Update()
            reslices[i] = reslice
        for window in windows:
            window.Render()
    else:
        for interactorStyle in interactorStyles:
            interactorStyle.OnMouseMove()


def slice_visualisation(file_paths):
    name = ["IRM1", "IRM2", "Segmentation 1", "Segmentation 2"]

    global interactors, windows, reslices
    colors = []
    
    for i, file_path in enumerate(file_paths):
        reader = vtk.vtkNrrdReader()
        reader.SetFileName(file_path)
        reader.Update()
        
        (xMin, xMax, yMin, yMax, zMin, zMax) = reader.GetExecutive().GetWholeExtent(reader.GetOutputInformation(0))
        (xSpacing, ySpacing, zSpacing) = reader.GetOutput().GetSpacing()
        (x0, y0, z0) = reader.GetOutput().GetOrigin()


        center = [(x0 + xSpacing * 0.5 * (xMin + xMax)),
                (y0 + ySpacing * 0.5 * (yMin + yMax)),
                (z0 + zSpacing * 0.5 * (zMin + zMax))]
        axial = vtk.vtkMatrix4x4()
        axial.DeepCopy((1, 0, 0, center[0],
                        0, 0, 1, center[1],
                        0, -1, 0, center[2],
                        0, 0, 0, 1))

        # Extract a slice in the desired orientation
        reslice = vtk.vtkImageReslice()
        reslice.SetInputConnection(reader.GetOutputPort())
        reslice.SetOutputDimensionality(2)
        reslice.SetResliceAxes(axial)
        reslice.SetInterpolationModeToLinear() 

        reslices.append(reslice)


        # Create a greyscale lookup table
        table = vtk.vtkLookupTable()
        
        if (i < 2):
            table.SetRange(0, 2000)
            table.SetValueRange(0.0, 1.0)
            table.SetSaturationRange(0.0, 0.0)
            table.SetRampToLinear()
        else:
            table.SetTableValue(0,[0.0,0.0,0.0,1.0])
            table.SetTableValue(255,[1.0,1.0,0.0,1.0])
        table.Build()

        # Map the image through the lookup table
        color = vtk.vtkImageMapToColors()
        color.SetLookupTable(table)
        color.SetInputConnection(reslice.GetOutputPort())
        colors.append(color)
        
    for i in range(4):
        blend = colors[i]
        if (i>1):
            blend = vtk.vtkImageBlend()
            blend.AddInputConnection(colors[i-2].GetOutputPort())
            blend.AddInputConnection(colors[i].GetOutputPort())
            blend.SetOpacity(0, 0.7);
            blend.SetOpacity(1, 0.5);

        actor = vtk.vtkImageActor()
        actor.GetMapper().SetInputConnection(blend.GetOutputPort())

        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderers.append(renderer)
        renderers.append(renderer)
        windows[i].AddRenderer(renderer)
        windows[i].SetWindowName(f"{name[i]}")

def synchronize_cameras(renderer1, renderer2):
    def on_camera_modified(caller, event):
        if event == "ModifiedEvent":
            camera1 = renderer1.GetActiveCamera()
            camera2 = renderer2.GetActiveCamera()
            camera2.DeepCopy(camera1)
            renderer2.GetRenderWindow().Render()

    renderer1.GetRenderWindow().GetInteractor().AddObserver("EndInteractionEvent", on_camera_modified)
    renderer2.GetRenderWindow().GetInteractor().AddObserver("EndInteractionEvent", on_camera_modified)


def mod_visualisation(filePaths):
    colors = vtk.vtkNamedColors()
    camera = vtk.vtkCamera()
 
    name = ["modelisation 3D seg1", "modelisation 3D seg2"]
    volumes = get_volumes_list(filePaths)
    for i in range(4,6):
        window = windows[i]
        window.SetWindowName(f"{name[i-4]}")
        renderer = vtk.vtkRenderer()
        renderer.SetActiveCamera(camera)
        
        renderer.AddActor(volumes[i-4])
        renderer.SetBackground(colors.GetColor3d("Seashell"))

        renderer.ResetCamera()
        renderers.append(renderer)
        window.AddRenderer(renderer)
    synchronize_cameras(renderers[4],renderers[5])


def compute_tumor_volume(seg):
    # the spacing of the image is [1,1,1]
    return np.count_nonzero(seg)

def compute_mean_intensity(image, seg):
    return np.mean(image[seg != 0])


def results_visualisation(seg1, seg2, image1, image2):
    colors = vtk.vtkNamedColors()
    renderer = vtk.vtkRenderer()
    window = windows[6]
    window.AddRenderer(renderer)
    windows[6].SetWindowName("Quantitative results")
    windows[6].SetSize(600,500)
    text_actor = vtk.vtkTextActor()

    volume_gre1 = compute_tumor_volume(seg1)
    volume_gre2 = compute_tumor_volume(seg2)

    intensity_gre1 = compute_mean_intensity(image1, seg1)
    intensity_gre2 = compute_mean_intensity(image2, seg2)

    text_actor.SetInput(  f" Volume gre1: {volume_gre1}\n\n"
                        + f" Volume gre2: {volume_gre2}\n\n"
                        + f" Difference between volumes: {np.abs(volume_gre1 - volume_gre2)/10 * 10}\n\n\n"
                        + f" Intensity gre1: {intensity_gre1}\n\n"
                        + f" Intensity gre2: {intensity_gre2}\n\n"
                        + f" Difference between intensity: {np.abs(intensity_gre2 - intensity_gre1)/10 *10}\n\n\n")
    text_actor.GetTextProperty().SetFontSize(24)
    text_actor.GetTextProperty().SetColor(0, 0, 0)
    renderer.AddActor(text_actor)
    renderer.SetBackground(colors.GetColor3d("Seashell"))

def render_windows():
    w = 400
    h = 400
    for i in range(len(windows) - 1):
        windows[i].SetPosition(h - (i // 3) * h,(i % 3) * w)
        windows[i].Render()
    windows[6].SetPosition(800,0)
    windows[6].Render()

def visualize(file_paths_slice, file_paths_mod, seg1, seg2, image1, image2):
    print("Press any key to leave the application")
    init_windows(7)
    
    slice_visualisation(file_paths_slice)

    mod_visualisation(file_paths_mod)

    results_visualisation(seg1, seg2, image1, image2)

    IRM1 = windows[0]
    IRM2 = windows[1]
    SEG1 = windows[2]
    SEG2 = windows[3]
    MOD1 = windows[4]
    MOD2 = windows[5]
    INFO = windows[6]

    windows[3] = IRM1
    windows[4] = SEG1
    windows[5] = MOD1
    windows[0] = IRM2
    windows[1] = SEG2
    windows[2] = MOD2
    windows[6] = INFO

    render_windows()
    while(True):
        for interactor in interactors:
            interactor.ProcessEvents()
            interactor.Render()


if __name__ == "__main__":
    file_paths_slice = ["Data/case6_gre1.nrrd", "Data/case6_gre1.nrrd","seg_gre1_01.nrrd", "Data/case6_gre1.nrrd"]
    file_paths_mod = ["seg_gre1_01.nrrd", "seg_gre1_01.nrrd"]

    visualize(file_paths_slice, file_paths_mod)