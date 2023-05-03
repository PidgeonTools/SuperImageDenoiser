import bpy
import os
from math import ceil
from bpy.types import NodeTree
from ..SID_Settings import SID_Settings

def create_temporal_median(Minimum: bool) -> NodeTree:
    #Create median value node group
    if Minimum:
        MinOrMax = "MINIMUM"
        MedianName = ".MedianMin"
    else:
        MinOrMax = "MAXIMUM"
        MedianName = ".MedianMax"

    median_value_tree: NodeTree = bpy.data.node_groups.new(type="CompositorNodeTree", name=MedianName)
    median_value_tree_input = median_value_tree.nodes.new("NodeGroupInput")

    median_value_tree.inputs.new("NodeSocketColor", "a")
    median_value_tree.inputs.new("NodeSocketColor", "b")
    median_value_tree.outputs.new("NodeSocketColor", "Median Image")

    separate_color_0 = median_value_tree.nodes.new(type="CompositorNodeSeparateColor")
    separate_color_1 = median_value_tree.nodes.new(type="CompositorNodeSeparateColor")
    median_r = median_value_tree.nodes.new(type="CompositorNodeMath")
    median_r.operation = MinOrMax
    meidan_g = median_value_tree.nodes.new(type="CompositorNodeMath")
    meidan_g.operation = MinOrMax
    median_b = median_value_tree.nodes.new(type="CompositorNodeMath")
    median_b.operation = MinOrMax
    median_a = median_value_tree.nodes.new(type="CompositorNodeMath")
    median_a.operation = MinOrMax

    combine_color = median_value_tree.nodes.new(type="CompositorNodeCombineColor")
    median_value_tree_output = median_value_tree.nodes.new("NodeGroupOutput")

    # Link nodes
    median_value_tree.links.new(median_value_tree_input.outputs["a"],separate_color_0.inputs[0])
    median_value_tree.links.new(median_value_tree_input.outputs["b"],separate_color_1.inputs[0])
    
    median_value_tree.links.new(separate_color_0.outputs[0],median_r.inputs[0])
    median_value_tree.links.new(separate_color_0.outputs[1],meidan_g.inputs[0])
    median_value_tree.links.new(separate_color_0.outputs[2],median_b.inputs[0])
    median_value_tree.links.new(separate_color_0.outputs[3],median_a.inputs[0])

    median_value_tree.links.new(separate_color_1.outputs[0],median_r.inputs[1])
    median_value_tree.links.new(separate_color_1.outputs[1],meidan_g.inputs[1])
    median_value_tree.links.new(separate_color_1.outputs[2],median_b.inputs[1])
    median_value_tree.links.new(separate_color_1.outputs[3],median_a.inputs[1])

    median_value_tree.links.new(median_r.outputs[0],combine_color.inputs[0])
    median_value_tree.links.new(meidan_g.outputs[0],combine_color.inputs[1])
    median_value_tree.links.new(median_b.outputs[0],combine_color.inputs[2])
    median_value_tree.links.new(median_a.outputs[0],combine_color.inputs[3])

    median_value_tree.links.new(combine_color.outputs[0],median_value_tree_output.inputs['Median Image'])

    return median_value_tree

def create_temporal_align() -> NodeTree:
    #create temporal align node group
    settings: SID_Settings = bpy.context.scene.sid_settings
    align_tree: NodeTree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Align")
    align_tree_input = align_tree.nodes.new("NodeGroupInput")

    align_tree.inputs.new("NodeSocketColor", "Frame + 0")
    align_tree.inputs.new("NodeSocketVector", "Vector + 0")
    align_tree.inputs.new("NodeSocketColor", "Frame + 1")
    align_tree.inputs.new("NodeSocketVector", "Vector + 1")
    align_tree.inputs.new("NodeSocketFloat", "Depth + 1")
    align_tree.inputs.new("NodeSocketColor", "Frame + 2")
    align_tree.inputs.new("NodeSocketVector", "Vector + 2")

    align_tree.outputs.new("NodeSocketColor", "Temporal Aligned")

    displace_frame_0 = align_tree.nodes.new(type="CompositorNodeDisplace")
    displace_frame_0.inputs["X Scale"].default_value = -1
    displace_frame_0.inputs["Y Scale"].default_value = -1

    displace_frame_2 = align_tree.nodes.new(type="CompositorNodeDisplace")
    displace_frame_2.inputs["X Scale"].default_value = 1
    displace_frame_2.inputs["Y Scale"].default_value = 1

    median_max_0 = align_tree.nodes.new("CompositorNodeGroup")
    median_max_0.node_tree = create_temporal_median(False)

    median_min_2 = align_tree.nodes.new("CompositorNodeGroup")
    median_min_2.node_tree = create_temporal_median(True)

    median_min_a = align_tree.nodes.new("CompositorNodeGroup")
    median_min_a.node_tree = create_temporal_median(True)

    median_max_a = align_tree.nodes.new("CompositorNodeGroup")
    median_max_a.node_tree = create_temporal_median(False)

    alpha_over = align_tree.nodes.new("CompositorNodeAlphaOver")

    vecblur_node = align_tree.nodes.new("CompositorNodeVecBlur")
    vecblur_node.mute = not settings.SIDT_MB_Toggle
    vecblur_node.samples = settings.SIDT_MB_Samples
    vecblur_node.factor = settings.SIDT_MB_Shutter
    vecblur_node.speed_min = settings.SIDT_MB_Min
    vecblur_node.speed_max = settings.SIDT_MB_Max
    vecblur_node.use_curved = settings.SIDT_MB_Interpolation

    if settings.SIDT_Overscan_Amount > 0:
        render = bpy.context.scene.render
        overscan_percentage = ceil(render.resolution_percentage * (100 + settings.SIDT_Overscan_Amount) / 100)
        crop_aspect = (1 - (render.resolution_x * render.resolution_percentage / 100) / (render.resolution_x * overscan_percentage / 100)) / 2

        crop_node = align_tree.nodes.new("CompositorNodeCrop")
        crop_node.use_crop_size = True
        crop_node.relative = True
        crop_node.rel_min_x = crop_aspect
        crop_node.rel_max_x = 1 - crop_aspect
        crop_node.rel_min_y = crop_node.rel_min_x
        crop_node.rel_max_y = crop_node.rel_max_x

        scale_node = align_tree.nodes.new("CompositorNodeScale")
        scale_node.space = "ABSOLUTE"
        scale_node.inputs[1].default_value = render.resolution_x * render.resolution_percentage / 100
        scale_node.inputs[2].default_value = render.resolution_y * render.resolution_percentage / 100

    align_tree_output = align_tree.nodes.new("NodeGroupOutput")

    # Link nodes
    align_tree.links.new(align_tree_input.outputs["Frame + 0"],displace_frame_0.inputs[0])
    align_tree.links.new(align_tree_input.outputs["Vector + 0"],displace_frame_0.inputs[1])
    
    align_tree.links.new(align_tree_input.outputs["Frame + 2"],displace_frame_2.inputs[0])
    align_tree.links.new(align_tree_input.outputs["Vector + 2"],displace_frame_2.inputs[1])
    
    align_tree.links.new(align_tree_input.outputs["Frame + 1"],median_max_0.inputs[0])
    align_tree.links.new(displace_frame_2.outputs[0],median_max_0.inputs[1])
    
    align_tree.links.new(align_tree_input.outputs["Frame + 1"],median_min_2.inputs[0])
    align_tree.links.new(displace_frame_2.outputs[0],median_min_2.inputs[1])
    
    align_tree.links.new(median_max_0.outputs[0],median_min_a.inputs[0])
    align_tree.links.new(displace_frame_0.outputs[0],median_min_a.inputs[1])
    
    align_tree.links.new(median_min_a.outputs[0],median_max_a.inputs[0])
    align_tree.links.new(median_min_2.outputs[0],median_max_a.inputs[1])
    
    align_tree.links.new(align_tree_input.outputs["Frame + 1"],alpha_over.inputs[1])
    align_tree.links.new(median_max_a.outputs[0],alpha_over.inputs[2])
    
    align_tree.links.new(alpha_over.outputs[0],vecblur_node.inputs[0])
    align_tree.links.new(align_tree_input.outputs["Depth + 1"],vecblur_node.inputs[1])
    align_tree.links.new(align_tree_input.outputs["Vector + 1"],vecblur_node.inputs[2])
    
    if settings.SIDT_Overscan_Amount == 0:
        align_tree.links.new(vecblur_node.outputs[0],align_tree_output.inputs["Temporal Aligned"])
    else:
        align_tree.links.new(vecblur_node.outputs[0],crop_node.inputs[0])
        align_tree.links.new(crop_node.outputs[0],scale_node.inputs[0])
        align_tree.links.new(scale_node.outputs[0],align_tree_output.inputs["Temporal Aligned"])

    return align_tree

def create_temporal_setup(scene,settings,view_layer_id):
    #setup node groups
    print("CURRENTLY WORKING ON VIEW LAYER: " + f"{view_layer_id}")
    ntree = scene.node_tree
    settings.inputdir = bpy.path.abspath(settings.inputdir)
    path_noisy = os.path.join(settings.inputdir, "noisy", f"{view_layer_id}")
    path_denoised = os.path.join(settings.inputdir, "denoised", f"{view_layer_id}")

    # Clear Compositor Output
    for node in ntree.nodes: ntree.nodes.remove(node)
    
    #count files rendered
    file_count = 0
    for file in os.listdir(path_noisy):
        if file.endswith(".exr"):
            file_count += 1

    old_frame_start = scene.frame_start
    scene.frame_start = 1
    scene.frame_end = file_count - 3
    scene.frame_current = 1

    Frame_0 = ntree.nodes.new(type="CompositorNodeImage")
    Frame_0.image = bpy.data.images.load(os.path.join(path_noisy , str(old_frame_start).zfill(6) + ".exr"))
    Frame_0.image.source = "SEQUENCE"
    Frame_0.frame_duration = file_count
    Frame_0.frame_start = 1
    Frame_0.frame_offset = 0 + old_frame_start

    Frame_1 = ntree.nodes.new(type="CompositorNodeImage")
    Frame_1.image = Frame_0.image
    Frame_1.frame_duration = Frame_0.frame_duration
    Frame_1.frame_start = Frame_0.frame_start
    Frame_1.frame_offset = 1 + old_frame_start

    Frame_2 = ntree.nodes.new(type="CompositorNodeImage")
    Frame_2.image = Frame_0.image
    Frame_2.frame_duration = Frame_0.frame_duration
    Frame_2.frame_start = Frame_0.frame_start
    Frame_2.frame_offset = 2 + old_frame_start

    def link_to_node(inputNode, Layer, outNode):
        ntree.links.new(Frame_0.outputs[Layer], inputNode.inputs["Frame + 0"])
        ntree.links.new(Frame_0.outputs["Vector"], inputNode.inputs["Vector + 0"])
        
        ntree.links.new(Frame_1.outputs[Layer], inputNode.inputs["Frame + 1"])
        ntree.links.new(Frame_1.outputs["Vector"], inputNode.inputs["Vector + 1"])
        ntree.links.new(Frame_1.outputs["Depth"], inputNode.inputs["Depth + 1"])
        
        ntree.links.new(Frame_2.outputs[Layer], inputNode.inputs["Frame + 2"])
        ntree.links.new(Frame_2.outputs["Vector"], inputNode.inputs["Vector + 2"])
        
        ntree.links.new(inputNode.outputs[0], outNode.inputs[Layer])

    TempAlign = ntree.nodes.new("CompositorNodeGroup")
    TempAlign.node_tree = create_temporal_align()
    
    OutputNode = ntree.nodes.new(type="CompositorNodeComposite")
    
    link_to_node(TempAlign, "Image", OutputNode)

    if settings.SIDT_mlEXR:
        settings.SIDT_File_Format = "JPEG"

        EXROutputNode = ntree.nodes.new(type='CompositorNodeOutputFile')
        EXROutputNode.name = "mlEXR Node"
        EXROutputNode.base_path = os.path.join(path_denoised, "mlEXR", "######")
        EXROutputNode.format.file_format = 'OPEN_EXR_MULTILAYER'
        # Image
        link_to_node(TempAlign, "Image", EXROutputNode)
        # Diffuse
        TempAlignDiffuse = ntree.nodes.new("CompositorNodeGroup")
        TempAlignDiffuse.node_tree = create_temporal_align()
        EXROutputNode.file_slots.new("Diffuse")
        link_to_node(TempAlignDiffuse, "Diffuse", EXROutputNode)
        # Glossy
        TempAlignGlossy = ntree.nodes.new("CompositorNodeGroup")
        TempAlignGlossy.node_tree = create_temporal_align()
        EXROutputNode.file_slots.new("Glossy")
        link_to_node(TempAlignGlossy, "Glossy", EXROutputNode)
        # Transmission
        if settings.use_transmission:
            TempAlignTransmission = ntree.nodes.new("CompositorNodeGroup")
            TempAlignTransmission.node_tree = create_temporal_align()
            EXROutputNode.file_slots.new("Transmission")
            link_to_node(TempAlignTransmission, "Transmission", EXROutputNode)
        # Volume
        if settings.use_volumetric:
            TempAlignVolume = ntree.nodes.new("CompositorNodeGroup")
            TempAlignVolume.node_tree = create_temporal_align()
            EXROutputNode.file_slots.new("Volume")
            link_to_node(TempAlignVolume, "Volume", EXROutputNode)
        # Emission
        if settings.use_emission:
            TempAlignEmission = ntree.nodes.new("CompositorNodeGroup")
            TempAlignEmission.node_tree = create_temporal_align()
            EXROutputNode.file_slots.new("Emission")
            link_to_node(TempAlignEmission, "Emission", EXROutputNode)
        # Environment
        if settings.use_environment:
            TempAlignEnvironment = ntree.nodes.new("CompositorNodeGroup")
            TempAlignEnvironment.node_tree = create_temporal_align()
            EXROutputNode.file_slots.new("Env")
            link_to_node(TempAlignEnvironment, "Env", EXROutputNode)
            
    # Set up render
    scene.render.filepath = os.path.join(path_denoised, "######")
    scene.render.image_settings.file_format = settings.SIDT_File_Format

    # PNG
    if settings.SIDT_File_Format == "PNG":
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '8'
        scene.render.image_settings.compression = 0
    # JPEG
    elif settings.SIDT_File_Format == "JPEG":
        scene.render.image_settings.color_mode = 'RGB'
        scene.render.image_settings.quality = 90
    # EXR
    elif settings.SIDT_File_Format == "OPEN_EXR":
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '32'
        scene.render.image_settings.exr_codec = 'ZIP'

    # Render
    bpy.ops.render.render(animation = True, scene = scene.name)

