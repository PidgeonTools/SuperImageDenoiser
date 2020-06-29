<<<<<<< HEAD
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
    # TODO: better name?
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

=======
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

from SID_Create_DenoiserGroup import create_sid_super_denoiser_group
from SID_QualityStandart import create_sid_denoiser_standard
from SID_QualityHigh import create_sid_denoiser_high
from SID_QualitySuper import create_sid_denoiser_super
from SID_Settings import SID_Settings



def create_sid_super_group(standard_denoiser_tree, high_denoiser_tree, super_denoiser_tree, settings: SID_Settings):
    # TODO: better name?
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

>>>>>>> dc9e23cd6ac552f0b0ae285cb0a5bad03d5a1716
    return SID_super_group