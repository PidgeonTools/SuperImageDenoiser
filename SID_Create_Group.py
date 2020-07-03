import bpy

from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty,
)
from . import SID_Settings

def create_sid_super_group(standard_denoiser_tree, high_denoiser_tree, super_denoiser_tree, settings: SID_Settings):

    SID_super_group = bpy.data.node_groups.new(type='CompositorNodeTree', name=".SuperImageDenoiser.SuperGroup")
    input_node = SID_super_group.nodes.new("NodeGroupInput")
    input_node.location = (-200, 0)

    output_node = SID_super_group.nodes.new("NodeGroupOutput")
    output_node.location = (1800, 0)

    SID_super_group.inputs.new("NodeSocketColor", "Noisy Image")
    SID_super_group.inputs.new("NodeSocketVector", "Denoising Normal")
    SID_super_group.inputs.new("NodeSocketColor", "Denoising Albedo")
    SID_super_group.inputs.new("NodeSocketColor", "Alpha")
    SID_super_group.inputs.new("NodeSocketColor", "DiffDir")
    SID_super_group.inputs.new("NodeSocketColor", "DiffInd")
    SID_super_group.inputs.new("NodeSocketColor", "DiffCol")
    SID_super_group.inputs.new("NodeSocketColor", "GlossDir")
    SID_super_group.inputs.new("NodeSocketColor", "GlossInd")
    SID_super_group.inputs.new("NodeSocketColor", "GlossCol")
    if settings.use_transmission:
        SID_super_group.inputs.new("NodeSocketColor", "TransDir")
        SID_super_group.inputs.new("NodeSocketColor", "TransInd")
        SID_super_group.inputs.new("NodeSocketColor", "TransCol")
    if settings.use_volumetric:
        SID_super_group.inputs.new("NodeSocketColor", "VolumeDir")
        SID_super_group.inputs.new("NodeSocketColor", "VolumeInd")
    if settings.use_emission:
        SID_super_group.inputs.new("NodeSocketColor", "Emit")
    if settings.use_environment:
        SID_super_group.inputs.new("NodeSocketColor", "Env")

    SID_super_group.outputs.new("NodeSocketColor", "Standard Quality")
    SID_super_group.outputs.new("NodeSocketColor", "High Quality")
    SID_super_group.outputs.new("NodeSocketColor", "SUPER Quality")

    if settings.use_mlEXR:
        SID_super_group.outputs.new("NodeSocketColor", "DN Diffuse")
        SID_super_group.outputs.new("NodeSocketColor", 'DN Glossy')
        SID_super_group.outputs.new("NodeSocketColor", 'DN Transmission')
        if settings.use_volumetric:
            SID_super_group.outputs.new("NodeSocketColor", 'DN Volume')
        if settings.use_emission:
            SID_super_group.outputs.new("NodeSocketColor", 'Emission')
        if settings.use_environment:
            SID_super_group.outputs.new("NodeSocketColor", "Envrionment")



    standard_denoiser_node = SID_super_group.nodes.new("CompositorNodeGroup")
    standard_denoiser_node.node_tree = standard_denoiser_tree
    standard_denoiser_node.location = (0, 900)
    standard_denoiser_node.name = standard_denoiser_node.label = "Standard Denoiser"

    high_denoiser_node = SID_super_group.nodes.new("CompositorNodeGroup")
    high_denoiser_node.node_tree = high_denoiser_tree
    high_denoiser_node.location = (0, 600)
    high_denoiser_node.name = high_denoiser_node.label = "High Quality Denoiser"

    super_denoiser_node = SID_super_group.nodes.new("CompositorNodeGroup")
    super_denoiser_node.node_tree = super_denoiser_tree
    super_denoiser_node.location = (0, 0)
    super_denoiser_node.name = super_denoiser_node.label = "SUPER Denoiser"


    # Standard
    input_sockets = [
        "Noisy Image",
        "Denoising Normal",
        "Denoising Albedo",
    ]
    for input in input_sockets:
        SID_super_group.links.new(input_node.outputs[input], standard_denoiser_node.inputs[input])

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
        SID_super_group.links.new(input_node.outputs[input], super_denoiser_node.inputs[input])
        SID_super_group.links.new(input_node.outputs[input], high_denoiser_node.inputs[input])


    SID_super_group.links.new(standard_denoiser_node.outputs['Denoised Image'], output_node.inputs['Standard Quality'])
    SID_super_group.links.new(high_denoiser_node.outputs['Denoised Image'], output_node.inputs['High Quality'])
    SID_super_group.links.new(super_denoiser_node.outputs['Denoised Image'], output_node.inputs['SUPER Quality'])

    if settings.use_mlEXR:
        if settings.quality == "HIGH":
            DenoiserType = high_denoiser_node
        elif settings.quality == "SUPER":
            DenoiserType = super_denoiser_node

        SID_super_group.links.new(DenoiserType.outputs['DN Diffuse'], output_node.inputs['DN Diffuse'])
        SID_super_group.links.new(DenoiserType.outputs['DN Glossy'], output_node.inputs['DN Glossy'])
        SID_super_group.links.new(DenoiserType.outputs['DN Transmission'], output_node.inputs['DN Transmission'])
        if settings.use_volumetric:
            SID_super_group.links.new(DenoiserType.outputs['DN Volume'], output_node.inputs['DN Volume'])
        if settings.use_emission:
            SID_super_group.links.new(DenoiserType.outputs['Emission'], output_node.inputs['Emission'])
        if settings.use_environment:
            SID_super_group.links.new(DenoiserType.outputs["Envrionment"], output_node.inputs["Envrionment"])


    return SID_super_group