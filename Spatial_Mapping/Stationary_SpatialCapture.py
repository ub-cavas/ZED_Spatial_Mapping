#import pyzed.sl as sl

# Create a Camera object
zed = sl.Camera()

# Configure spatial mapping parameters
mapping_parameters = sl.SpatialMappingParameters(sl.MAPPING_RESOLUTION.LOW,
                                                 sl.MAPPING_RANGE.FAR)
mapping_parameters.map_type = sl.MAP_TYPE.MESH
mapping_parameters.save_texture = True
filter_params = sl.MeshFilterParameters() # not available for fused point cloud
filter_params.set(sl.MESH_FILTER.LOW) # not available for fused point cloud

# Enable tracking and mapping
tracking_parameters = sl.TrackingParameters()


zed.enable_tracking(tracking_parameters)
zed.enable_spatial_mapping(mapping_parameters)

mesh = sl.Mesh() # Create a mesh object
timer = 0

# Grab 500 frames and stop
while timer < 500 :
  if zed.grab() == sl.ERROR_CODE.SUCCESS :
    # When grab() = SUCCESS, a new image, depth and pose is available.
    # Spatial mapping automatically ingests the new data to build the mesh.
    timer += 1

# Retrieve the spatial map
zed.extract_whole_spatial_map(mesh)
# Filter the mesh
mesh.filter(filter_params) # not available for fused point cloud
# Apply the texture
mesh.apply_texture() # not available for fused point cloud
# Save the mesh in .obj format
mesh.save("stationary_mesh.obj")