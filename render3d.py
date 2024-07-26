import vtk

def volumize(filePath,itkImage=None,x_location=0):# \
    #-> type:
    """ description
    Args 
    ----
    nom arg: type
        desc

    Returns
    -------
    type
        desc

    """
    # Read the data from a Nrrd file
    reader = vtk.vtkNrrdReader()
    reader.SetFileName(filePath)

    #source = itk.vtk_image_from_image(itkImage)
    
    # Create transfer functions for opacity and color
    opacity_transfer_function = vtk.vtkPiecewiseFunction()
    opacity_transfer_function.AddPoint(20, 0.0)
    opacity_transfer_function.AddPoint(255, 0.3)

    color_transfer_function = vtk.vtkColorTransferFunction()
    color_transfer_function.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
    color_transfer_function.AddRGBPoint(64.0, 1.0, 0.0, 0.0)
    color_transfer_function.AddRGBPoint(128.0, 0.0, 0.0, 1.0)
    color_transfer_function.AddRGBPoint(192.0, 0.0, 1.0, 0.0)
    color_transfer_function.AddRGBPoint(255.0, 0.0, 0.2, 0.0)

    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_transfer_function)
    volume_property.SetScalarOpacity(opacity_transfer_function)


    volume_mapper = vtk.vtkSmartVolumeMapper()

    volume_mapper.SetInputConnection(reader.GetOutputPort())

    volume = vtk.vtkVolume()
    volume.SetMapper(volume_mapper)
    volume.SetProperty(volume_property)
    transform = vtk.vtkTransform()

    transform.Translate([x_location, 0, 0])

    matrix = transform.GetMatrix()
   
    volume.SetUserMatrix(matrix)
    return volume

def get_volumes_list(filePaths):# [str]) \
    #-> type:
    """ description
    Args 
    ----
    nom arg: type
        desc

    Returns
    -------
    type
        desc

    """
    volumes = []
    for i,filePath in enumerate(filePaths):
        volumes.append(volumize(filePath, x_location=i*26))
    return volumes

def main():
    colors =  vtk.vtkNamedColors()
    # Have some fun with colors
    ren_bkg = ['Seashell', 'Seashell', 'Seashell']

    # Window sizes and spacing.
    width = 300
    height = 300
    # Add extra space around each window.
    dx = 20
    dy = 40
    w = width + dx
    h = height + dy

    interactors = list()
    running = [True, True, True, True]

    camera = None
    name = ["n" , "n-(n+1)", "n+1"]
    volumes = get_volumes_list(["seg_gre1.nrrd","seg_gre2_registered.nrrd", "seg_gre1.nrrd"])

    kpis = list()
    for i in range(0, 3):
        ren_win = vtk.vtkRenderWindow()
        ren_win.SetSize(width, height)

        renderer = vtk.vtkRenderer()
        # Share the camera between viewports.
        if i == 0:
            camera = renderer.GetActiveCamera()
            camera.Azimuth(30)
            camera.Elevation(30)
        else:
            renderer.SetActiveCamera(camera)

        ren_win.AddRenderer(renderer)

        iren = vtk.vtkRenderWindowInteractor()

        interactors.append(iren)

        iren.SetRenderWindow(ren_win)
        ren_win.Render()
        ren_win.SetWindowName(f"{name[i]}")
        ren_win.SetPosition((i % 2) * w, h - (i // 2) * h)

        
        renderer.AddActor(volumes[i])
        renderer.SetBackground(colors.GetColor3d(ren_bkg[i]))

        renderer.ResetCamera()

        running[i] = True
        kpis.append(KeyPressInteractorStyle(parent=iren))
        interactors[i].SetInteractorStyle(kpis[i])
        kpis[i].status = running[i]

    interactors[0].Initialize()
    while all(x is True for x in running):
        for i in range(0, 3):
            running[i] = kpis[i].status
            if running[i]:
                interactors[i].ProcessEvents()
                interactors[i].Render()
            else:
                interactors[i].TerminateApp()
    else:
        interactors[0].Start()

class KeyPressInteractorStyle( vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None, status=True):
        self.parent =  vtk.vtkRenderWindowInteractor()
        self.status = status
        if parent is not None:
            self.parent = parent

        self.AddObserver('KeyPressEvent', self.key_press_event)

    def key_press_event(self, obj, event):
        key = self.parent.GetKeySym().lower()
        if key == 'e' or key == 'q':
            self.status = False
        return


if __name__ == '__main__':
    main()