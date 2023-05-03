import bpy
from bpy.types import NodeTree

from .. import SID_Settings

def create_cycles_group(
        standard_denoiser_tree: NodeTree,
        high_denoiser_tree: NodeTree,
        super_denoiser_tree : NodeTree,
        settings: SID_Settings
        ) -> NodeTree:

    sid_super_group: NodeTree = bpy.data.node_groups.new(
        type='CompositorNodeTree',
        name=".SuperImageDenoiser"
        )
    input_node = sid_super_group.nodes.new("NodeGroupInput")
    input_node.location = (-200, 0)

    output_node = sid_super_group.nodes.new("NodeGroupOutput")
    output_node.location = (1800, 0)
    # Base
    sid_super_group.inputs.new("NodeSocketColor", "Noisy Image")
    sid_super_group.inputs.new("NodeSocketVector", "Denoising Normal")
    sid_super_group.inputs.new("NodeSocketColor", "Denoising Albedo")
    sid_super_group.inputs.new("NodeSocketColor", "Alpha")
    # Diffuse
    sid_super_group.inputs.new("NodeSocketColor", "DiffDir")
    sid_super_group.inputs.new("NodeSocketColor", "DiffInd")
    sid_super_group.inputs.new("NodeSocketColor", "DiffCol")
    # Glossy
    sid_super_group.inputs.new("NodeSocketColor", "GlossDir")
    sid_super_group.inputs.new("NodeSocketColor", "GlossInd")
    sid_super_group.inputs.new("NodeSocketColor", "GlossCol")
    # Transmission
    if settings.use_transmission:
        sid_super_group.inputs.new("NodeSocketColor", "TransDir")
        sid_super_group.inputs.new("NodeSocketColor", "TransInd")
        sid_super_group.inputs.new("NodeSocketColor", "TransCol")
    # Volumetric
    if settings.use_volumetric:
        sid_super_group.inputs.new("NodeSocketColor", "VolumeDir")
        sid_super_group.inputs.new("NodeSocketColor", "VolumeInd")
    # Emission
    if settings.use_emission:
        sid_super_group.inputs.new("NodeSocketColor", "Emit")
    # Environment
    if settings.use_environment:
        sid_super_group.inputs.new("NodeSocketColor", "Env")

    # Quality
    sid_super_group.outputs.new("NodeSocketColor", "Standard Quality")
    sid_super_group.outputs.new("NodeSocketColor", "High Quality")
    sid_super_group.outputs.new("NodeSocketColor", "SUPER Quality")

    # mlEXR
    sid_super_group.outputs.new("NodeSocketColor", "DN Diffuse")
    sid_super_group.outputs.new("NodeSocketColor", 'DN Glossy')
    if settings.use_transmission: sid_super_group.outputs.new("NodeSocketColor", 'DN Transmission')
    if settings.use_volumetric: sid_super_group.outputs.new("NodeSocketColor", 'DN Volume')
    if settings.use_emission: sid_super_group.outputs.new("NodeSocketColor", 'Emission')
    if settings.use_environment: sid_super_group.outputs.new("NodeSocketColor", "Environment")

    # Standard
    standard_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
    standard_denoiser_node.node_tree = standard_denoiser_tree
    standard_denoiser_node.location = (0, 900)
    standard_denoiser_node.name = standard_denoiser_node.label = "Standard Denoiser"
    input_sockets = [
        "Noisy Image",
        "Denoising Normal",
        "Denoising Albedo",
    ]
    for input in input_sockets: sid_super_group.links.new(input_node.outputs[input],standard_denoiser_node.inputs[input])

    # High
    high_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
    high_denoiser_node.node_tree = high_denoiser_tree
    high_denoiser_node.location = (0, 600)
    high_denoiser_node.name = high_denoiser_node.label = "High Quality Denoiser"
    # SUPER
    super_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
    super_denoiser_node.node_tree = super_denoiser_tree
    super_denoiser_node.location = (0, 0)
    super_denoiser_node.name = super_denoiser_node.label = "SUPER Denoiser"

    # High & SUPER
    input_sockets = [
        "Noisy Image",
        "Denoising Normal",
        "Denoising Albedo",
        "Alpha",
        "DiffDir",
        "DiffInd",
        "DiffCol",
        "GlossDir",
        "GlossInd",
        "GlossCol",
    ]
    if settings.use_transmission:
        input_sockets.extend([
            "TransDir",
            "TransInd",
            "TransCol",
        ])
    if settings.use_volumetric:
        input_sockets.extend([
            "VolumeDir",
            "VolumeInd",
        ])
    if settings.use_emission:
        input_sockets.extend([
            "Emit",
        ])
    if settings.use_environment:
        input_sockets.extend([
            "Env",
        ])


    for input in input_sockets:
        sid_super_group.links.new(input_node.outputs[input],super_denoiser_node.inputs[input])
        sid_super_group.links.new(input_node.outputs[input],high_denoiser_node.inputs[input])


    sid_super_group.links.new(standard_denoiser_node.outputs['Denoised Image'],output_node.inputs['Standard Quality'])
    sid_super_group.links.new(high_denoiser_node.outputs['Denoised Image'],output_node.inputs['High Quality'])
    sid_super_group.links.new(super_denoiser_node.outputs['Denoised Image'],output_node.inputs['SUPER Quality'])

    if settings.quality != 'STANDARD':

        if settings.quality == "HIGH": denoiser_type = high_denoiser_node
        elif settings.quality == "SUPER": denoiser_type = super_denoiser_node

        # Diffuse
        sid_super_group.links.new(denoiser_type.outputs['Denoised Diffuse'],output_node.inputs['DN Diffuse'])
        # Glossy
        sid_super_group.links.new(denoiser_type.outputs['Denoised Glossy'],output_node.inputs['DN Glossy'])
        # Transmission
        if settings.use_transmission:
            sid_super_group.links.new(denoiser_type.outputs['Denoised Transmission'],output_node.inputs['DN Transmission'])
        # Volume
        if settings.use_volumetric:
            sid_super_group.links.new(denoiser_type.outputs['Denoised Volume'],output_node.inputs['DN Volume'])
        # Emission
        if settings.use_emission: sid_super_group.links.new(denoiser_type.outputs['Emission'],output_node.inputs['Emission'])
        # Environment
        if settings.use_environment: sid_super_group.links.new(denoiser_type.outputs["Environment"],output_node.inputs["Environment"])

    return sid_super_group
