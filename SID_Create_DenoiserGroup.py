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

from SID_Create_Group import create_sid_super_group
from SID_QualityStandart import create_sid_denoiser_standard
from SID_QualityHigh import create_sid_denoiser_high
from SID_QualitySuper import create_sid_denoiser_super
from SID_Settings import SID_Settings




def create_sid_super_denoiser_group(sid_denoiser_tree, settings: SID_Settings):
    # Creates a super denoiser node group using the provided subgroup

    SID_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SuperImageDenoiser")
    input_node = SID_tree.nodes.new("NodeGroupInput")
    input_node.location = (-200, 0)

    output_node = SID_tree.nodes.new("NodeGroupOutput")
    output_node.location = (1800, 0)

    SID_tree.inputs.new("NodeSocketColor", "Noisy Image")
    SID_tree.inputs.new("NodeSocketVector", "Denoising Normal")
    SID_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
    SID_tree.inputs.new("NodeSocketColor", "Alpha")

    # Add instances of the dual denoiser

    ##DIFFUSE##
    SID_tree.inputs.new("NodeSocketColor", "DiffDir")
    SID_tree.inputs.new("NodeSocketColor", "DiffInd")
    SID_tree.inputs.new("NodeSocketColor", "DiffCol")
    diffuse_denoiser_node = SID_tree.nodes.new("CompositorNodeGroup")
    diffuse_denoiser_node.node_tree = sid_denoiser_tree
    diffuse_denoiser_node.location = (0, 600)
    diffuse_denoiser_node.name = diffuse_denoiser_node.label = "Denoise Diffuse"

    # link nodes
    SID_tree.links.new(input_node.outputs['DiffDir'], diffuse_denoiser_node.inputs['Direct'])
    SID_tree.links.new(input_node.outputs['DiffInd'], diffuse_denoiser_node.inputs['Indirect'])
    SID_tree.links.new(input_node.outputs['DiffCol'], diffuse_denoiser_node.inputs['Color'])
    SID_tree.links.new(input_node.outputs['Denoising Normal'], diffuse_denoiser_node.inputs['Denoising Normal'])
    SID_tree.links.new(input_node.outputs['Denoising Albedo'], diffuse_denoiser_node.inputs['Denoising Albedo'])


    ##GLOSSY##
    SID_tree.inputs.new("NodeSocketColor", "GlossDir")
    SID_tree.inputs.new("NodeSocketColor", "GlossInd")
    SID_tree.inputs.new("NodeSocketColor", "GlossCol")
    glossy_denoiser_node = SID_tree.nodes.new("CompositorNodeGroup")
    glossy_denoiser_node.node_tree = sid_denoiser_tree
    glossy_denoiser_node.location = (0, 400)
    glossy_denoiser_node.name = glossy_denoiser_node.label = "Denoise Glossy"

    # Link nodes
    SID_tree.links.new(input_node.outputs['GlossDir'], glossy_denoiser_node.inputs['Direct'])
    SID_tree.links.new(input_node.outputs['GlossInd'], glossy_denoiser_node.inputs['Indirect'])
    SID_tree.links.new(input_node.outputs['GlossCol'], glossy_denoiser_node.inputs['Color'])
    SID_tree.links.new(input_node.outputs['Denoising Normal'], glossy_denoiser_node.inputs['Denoising Normal'])
    SID_tree.links.new(input_node.outputs['Denoising Albedo'], glossy_denoiser_node.inputs['Denoising Albedo'])


    ##TRANSMISSION##
    if settings.use_transmission:
        SID_tree.inputs.new("NodeSocketColor", "TransDir")
        SID_tree.inputs.new("NodeSocketColor", "TransInd")
        SID_tree.inputs.new("NodeSocketColor", "TransCol")
        transmission_denoiser_node = SID_tree.nodes.new("CompositorNodeGroup")
        transmission_denoiser_node.node_tree = sid_denoiser_tree
        transmission_denoiser_node.location = (0, 200)
        transmission_denoiser_node.name = transmission_denoiser_node.label = "Denoise Transmission"

        # Link nodes
        SID_tree.links.new(input_node.outputs['TransDir'], transmission_denoiser_node.inputs['Direct'])
        SID_tree.links.new(input_node.outputs['TransInd'], transmission_denoiser_node.inputs['Indirect'])
        SID_tree.links.new(input_node.outputs['TransCol'], transmission_denoiser_node.inputs['Color'])


    ##VOLUMES##
    if settings.use_volumetric:
        SID_tree.inputs.new("NodeSocketColor", "VolumeDir")
        SID_tree.inputs.new("NodeSocketColor", "VolumeInd")
        volume_denoiser_node = SID_tree.nodes.new("CompositorNodeGroup")
        volume_denoiser_node.node_tree = sid_denoiser_tree
        volume_denoiser_node.location = (0, 0)
        volume_denoiser_node.name = volume_denoiser_node.label = "Denoise Volume"

        # Link nodes
        SID_tree.links.new(input_node.outputs['VolumeDir'], volume_denoiser_node.inputs['Direct'])
        SID_tree.links.new(input_node.outputs['VolumeInd'], volume_denoiser_node.inputs['Indirect'])

    if settings.use_emission:
        SID_tree.inputs.new("NodeSocketColor", "Emit")

    if settings.use_environment:
        SID_tree.inputs.new("NodeSocketColor", "Env")


    ##ADD IT ALL TOGETHER##
    add_diffuse_glossy = SID_tree.nodes.new(type="CompositorNodeMixRGB")
    add_diffuse_glossy.blend_type = "ADD"
    add_diffuse_glossy.inputs[2].default_value = (0,0,0,1)
    add_diffuse_glossy.location = (200, 500)
    add_diffuse_glossy.name = add_diffuse_glossy.label = "Add Glossy"

    if settings.use_transmission:
        add_trans = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        add_trans.blend_type = "ADD"
        add_trans.inputs[2].default_value = (0,0,0,1)
        add_trans.location = (400, 400)
        add_trans.name = add_trans.label = "Add Transmission"

    if settings.use_volumetric:
        add_volume = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        add_volume.blend_type = "ADD"
        add_volume.inputs[2].default_value = (0,0,0,1)
        add_volume.location = (600, 300)
        add_volume.name = add_volume.label = "Add Volume"

    if settings.use_emission:
        emission_dn = SID_tree.nodes.new(type="CompositorNodeDenoise")
        emission_dn.location = (600, 100)
        emission_dn.name = emission_dn.label = "Denoise Emission"

        add_emission = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        add_emission.blend_type = "ADD"
        add_emission.inputs[2].default_value = (0,0,0,1)
        add_emission.location = (800, 200)
        add_emission.name = add_emission.label = "Add Emission"

    if settings.use_environment:
        add_environment = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        add_environment.blend_type = "ADD"
        add_environment.inputs[2].default_value = (0,0,0,1)
        add_environment.location = (1000, 100)
        add_environment.name = add_environment.label = "Add Environment"

    alpha_dn = SID_tree.nodes.new(type="CompositorNodeDenoise")
    alpha_dn.location = (1200, -100)
    alpha_dn.name = alpha_dn.label = "Denoise Alpha"

    final_dn = SID_tree.nodes.new(type="CompositorNodeDenoise")
    final_dn.location = (1200, 100)
    final_dn.name = final_dn.label = "Final Denoise"

    Seperate = SID_tree.nodes.new(type="CompositorNodeSepRGBA")
    Seperate.location = (1400, 100)
    Combine = SID_tree.nodes.new(type="CompositorNodeCombRGBA")
    Combine.location = (1600, 100)

    # Link nodes
    SID_tree.links.new(diffuse_denoiser_node.outputs['Denoised Image'], add_diffuse_glossy.inputs[1])
    SID_tree.links.new(glossy_denoiser_node.outputs['Denoised Image'], add_diffuse_glossy.inputs[2])
    prev_output = add_diffuse_glossy.outputs[0]

    if settings.use_transmission:
        SID_tree.links.new(prev_output, add_trans.inputs[1])
        SID_tree.links.new(transmission_denoiser_node.outputs['Denoised Image'], add_trans.inputs[2])
        prev_output = add_trans.outputs[0]

    if settings.use_volumetric:
        SID_tree.links.new(prev_output, add_volume.inputs[1])
        SID_tree.links.new(volume_denoiser_node.outputs['Denoised Image'], add_volume.inputs[2])
        prev_output = add_volume.outputs[0]

    if settings.use_emission:
        SID_tree.links.new(prev_output, add_emission.inputs[1])
        SID_tree.links.new(input_node.outputs['Emit'], emission_dn.inputs[0])
        SID_tree.links.new(emission_dn.outputs[0], add_emission.inputs[2])
        prev_output = add_emission.outputs[0]

    if settings.use_environment:
        SID_tree.links.new(prev_output, add_environment.inputs[1])
        SID_tree.links.new(input_node.outputs['Env'], add_environment.inputs[2])
        prev_output = add_environment.outputs[0]

    SID_tree.links.new(prev_output, final_dn.inputs[0])
    SID_tree.links.new(input_node.outputs['Denoising Normal'], final_dn.inputs[1])
    SID_tree.links.new(input_node.outputs['Denoising Albedo'], final_dn.inputs[2])
    SID_tree.links.new(input_node.outputs['Alpha'], alpha_dn.inputs[0])
    SID_tree.links.new(input_node.outputs['Denoising Normal'], alpha_dn.inputs[1])
    SID_tree.links.new(input_node.outputs['Denoising Albedo'], alpha_dn.inputs[2])

    SID_tree.outputs.new("NodeSocketColor", "Denoised Image")
    SID_tree.outputs.new("NodeSocketColor", "Denoised Diffuse")
    SID_tree.outputs.new("NodeSocketColor", "Denoised Glossy")

    if settings.use_transmission:
        SID_tree.outputs.new("NodeSocketColor", "Denoised Transmission")
        SID_tree.links.new(transmission_denoiser_node.outputs['Denoised Image'], output_node.inputs["Denoised Transmission"])
    if settings.use_volumetric:
        SID_tree.outputs.new("NodeSocketColor", "Denoised Volume")
        SID_tree.links.new(volume_denoiser_node.outputs['Denoised Image'], output_node.inputs["Denoised Volume"])

    SID_tree.links.new(Combine.outputs[0], output_node.inputs["Denoised Image"])
    SID_tree.links.new(diffuse_denoiser_node.outputs['Denoised Image'], output_node.inputs['Denoised Diffuse'])
    SID_tree.links.new(glossy_denoiser_node.outputs['Denoised Image'], output_node.inputs['Denoised Glossy'])
    SID_tree.links.new(Seperate.outputs["R"], Combine.inputs["R"])
    SID_tree.links.new(Seperate.outputs["G"], Combine.inputs["G"])
    SID_tree.links.new(Seperate.outputs["B"], Combine.inputs["B"])
    SID_tree.links.new(alpha_dn.outputs[0], Combine.inputs["A"])
    SID_tree.links.new(final_dn.outputs[0], Seperate.inputs[0])

    return SID_tree