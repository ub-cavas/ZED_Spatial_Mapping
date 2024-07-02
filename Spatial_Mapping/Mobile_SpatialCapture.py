import threading as th
#import pyzed.sl as sl

spatialMapUpdateFrames = 30
isCollectingZedData = True
mesh = sl.Mesh() # Create a mesh object
zed = sl.Camera() # Create a ZEDCamera object


#----------------------------------------------#
def Key_Capture_Thread():
   global isCollectingZedData
   while (input() != "STOP"):
      print("Collecting Camera Data")
   isCollectingZedData = False
   print

def Camera_Capture():
    global spatialMapUpdateFrames
    global isCollectingZedData
    global zed
    global mesh
    # Start keyboard interrupt thread
    th.Thread(target=Key_Capture_Thread, args=(), name="Key_Capture_Thread", daemon=True).start()
    timer = 0
    while isCollectingZedData:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            # Request an update of the spatial map every 30 frames (0.5s in HD720 mode)
            if timer % spatialMapUpdateFrames == 0 :
                zed.request_spatial_map_async()
            # Retrieve spatial_map when ready
            if zed.get_spatial_map_request_status_async() == sl.ERROR_CODE.SUCCESS and timer > 0:
                zed.retrieve_spatial_map_async(mesh)
            timer += 1

    print("Finished Collecting Camera Data!")

def main():
    global zed 
   

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.AUTO  # Use HD720 or HD1200 video mode (default fps: 60)
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init_params.coordinate_units = sl.UNIT.METER  # Set units in meters

    mapping_parameters = sl.SpatialMappingParameters(sl.MAPPING_RESOLUTION.LOW, sl.MAPPING_RANGE.FAR)
    mapping_parameters.map_type = sl.SPATIAL_MAP_TYPE.MESH
    mapping_parameters.save_texture = True # Scene texture will be recorded

    # Mesh filter parameters
    filter_params = sl.MeshFilterParameters() 
    filter_params.set(sl.MESH_FILTER.HIGH) 

    # Open the camera
    spatial_mapping_err = zed.open(init_params)
    if spatial_mapping_err != sl.ERROR_CODE.SUCCESS:
        print("Camera Open : "+repr(spatial_mapping_err)+". Exit program.")
        exit()

    # Enable positional tracking with default parameters.
    # Positional tracking needs to be enabled before using spatial mapping
    py_transform = sl.Transform()
    tracking_parameters = sl.PositionalTrackingParameters(_init_pos=py_transform)
    spatial_mapping_err = zed.enable_positional_tracking(tracking_parameters)
    if spatial_mapping_err != sl.ERROR_CODE.SUCCESS:
        print("Enable positional tracking : "+repr(spatial_mapping_err)+". Exit program.")
        zed.close()
        exit()

    # Enable tracking and spatial mapping
    mapping_parameters = sl.SpatialMappingParameters(map_type=sl.SPATIAL_MAP_TYPE.MESH)
    tracking_err = zed.enable_tracking(tracking_parameters)
    if tracking_err != s1.ERROR_CODE.SUCCESS:
        print("Enable tracking : "+repr(spatial_mapping_err)+". Exit program.")
        zed.close()
        exit(1)

    spatial_mapping_err = zed.enable_spatial_mapping(mapping_parameters)
    if spatial_mapping_err != sl.ERROR_CODE.SUCCESS:
        print("Enable spatial mapping : "+repr(spatial_mapping_err)+". Exit program.")
        zed.close()
        exit(1)

    print("\n")
    
    Camera_Capture()
    # Extract, filter and save the mesh in an obj file
    print("Extracting Mesh...\n")
    zed.extract_whole_spatial_map(mesh)
    # Filter the mesh
    print("Filtering Mesh...\n")
    mesh.filter(filter_params)
    # Apply the texture
    print("Applying textures... \n")
    mesh.apply_texture()
    # Save the mesh in .obj format
    print("Saving Mesh...\n")
    mesh.save("mobile_mesh.obj")

    # Disable tracking and mapping and close the camera
    zed.disable_spatial_mapping()
    zed.disable_positional_tracking()
    zed.close()


if __name__ == "__main__":
    main() 
