import threading as th
#import pyzed.sl as sl

#Set configuration parameters
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD720 # Use HD720 video mode (default fps: 60)
init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP # Use a right-handed Y-up coordinate system
init_params.coordinate_units = sl.UNIT.METER # Set units in meters
# Mapping parameters
spatialMapUpdateFrames = 30
mapping_parameters = sl.SpatialMappingParameters(sl.MAPPING_RESOLUTION.LOW, sl.MAPPING_RANGE.FAR)
mapping_parameters.map_type = sl.SPATIAL_MAP_TYPE.MESH
mapping_parameters.save_texture = True # Scene texture will be recorded
# Mesh filter parameters
filter_params = sl.MeshFilterParameters() 
filter_params.set(sl.MESH_FILTER.HIGH) 

tracking_parameters = sl.TrackingParameters()


#----------------------------------------------#
# Create a Camera object
zed = sl.Camera()
# Enable tracking and mapping
zed.enable_tracking(tracking_parameters)
zed.enable_spatial_mapping(mapping_parameters)

mesh = sl.Mesh() # Create a mesh object
isCollectingZedData = True

def Key_Capture_Thread():
   global isCollectingZedData
   while (input() != "STOP"):
      print("Collecting Camera Data")

   isCollectingZedData = False
   print

def Camera_Capture():
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
   

#---------RUNTIME--------------------#
Camera_Capture()
# Retrieve the spatial map
zed.extract_whole_spatial_map(mesh)
# Filter the mesh
mesh.filter(filter_params)
# Apply the texture
mesh.apply_texture()
# Save the mesh in .obj format
mesh.save("mobile_mesh.obj")