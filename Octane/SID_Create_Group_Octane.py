import bpy

from .. import SID_Settings

def create_Octane_group(
        standard_denoiser_tree,
        high_denoiser_tree,
        super_denoiser_tree,
        settings: SID_Settings
        ):
    sid_super_group = bpy.data.node_groups.new(
        type='CompositorNodeTree',
        name=".SuperImageDenoiser"
        )
    input_node = sid_super_group.nodes.new("NodeGroupInput")
    input_node.location = (-200, 0)

    output_node = sid_super_group.nodes.new("NodeGroupOutput")
    output_node.location = (1800, 0)

    sid_super_group.inputs.new("NodeSocketColor", "Noisy Image")
    sid_super_group.inputs.new("NodeSocketColor", "Alpha")
    if settings.use_emission:
        sid_super_group.inputs.new("NodeSocketColor", "Emission")
    sid_super_group.inputs.new("NodeSocketColor", "Diffuse")
    sid_super_group.inputs.new("NodeSocketColor", "Denoising Albedo")
    sid_super_group.inputs.new("NodeSocketColor", "Reflection")
    if settings.use_refraction:
        sid_super_group.inputs.new("NodeSocketColor", "Refraction")
    if settings.use_transmission:
        sid_super_group.inputs.new("NodeSocketColor", "Transmission")
    if settings.use_sss:
        sid_super_group.inputs.new("NodeSocketColor", "SSS")
    if settings.use_volumetric:
        sid_super_group.inputs.new("NodeSocketColor", "Volume")
        sid_super_group.inputs.new("NodeSocketColor", "VolumeEmission")
    sid_super_group.inputs.new("NodeSocketColor", "Denoising Normal")

    sid_super_group.outputs.new("NodeSocketColor", "Standard Quality")
    sid_super_group.outputs.new("NodeSocketColor", "High Quality")


    if settings.use_mlEXR:
        sid_super_group.outputs.new("NodeSocketColor", "DN Diffuse")
        sid_super_group.outputs.new("NodeSocketColor", 'DN Reflection')
        if settings.use_refraction:
            sid_super_group.outputs.new("NodeSocketColor", 'DN Refraction')
        if settings.use_transmission:
            sid_super_group.outputs.new("NodeSocketColor", 'DN Transmission')
        if settings.use_sss:
            sid_super_group.outputs.new("NodeSocketColor", 'DN SSS')
        if settings.use_emission:
            sid_super_group.outputs.new("NodeSocketColor", 'Emission')
        if settings.use_volumetric:
            sid_super_group.outputs.new("NodeSocketColor", 'DN Volume')
            sid_super_group.outputs.new("NodeSocketColor", 'DN VolumeEmission')
        sid_super_group.outputs.new("NodeSocketColor", 'Bad Pass')


    standard_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
    standard_denoiser_node.node_tree = standard_denoiser_tree
    standard_denoiser_node.location = (0, 900)
    standard_denoiser_node.name = standard_denoiser_node.label = "Standard Denoiser"

    high_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
    high_denoiser_node.node_tree = high_denoiser_tree
    high_denoiser_node.location = (0, 600)
    high_denoiser_node.name = high_denoiser_node.label = "High Quality Denoiser"

    #Standard
    input_sockets = [
        "Noisy Image",
        "Denoising Normal",
        "Denoising Albedo",
    ]
    for input in input_sockets:
        sid_super_group.links.new(
            input_node.outputs[input],
            standard_denoiser_node.inputs[input]
            )

    #High
    input_sockets = [
        "Noisy Image",
        "Denoising Albedo",
        "Denoising Normal",
        "Alpha",
        "Diffuse",
        "Reflection",
    ]
    if settings.use_transmission:
        input_sockets.extend([
            "Transmission",
        ])
    if settings.use_refraction:
        input_sockets.extend([
            "Refraction",
        ])
    if settings.use_volumetric:
        input_sockets.extend([
            "Volume",
            "VolumeEmission",
        ])
    if settings.use_emission:
        input_sockets.extend([
            "Emission",
        ])
    if settings.use_sss:
        input_sockets.extend([
            "SSS",
        ])


    for input in input_sockets:
        sid_super_group.links.new(
            input_node.outputs[input],
            high_denoiser_node.inputs[input]
            )

    sid_super_group.links.new(
        standard_denoiser_node.outputs['Denoised Image'],
        output_node.inputs['Standard Quality']
        )
    sid_super_group.links.new(
        high_denoiser_node.outputs['Denoised Image'],
        output_node.inputs['High Quality']
        )

    if settings.use_mlEXR and settings.quality != 'STANDARD':

        if settings.quality == "HIGH":
            denoiser_type = high_denoiser_node
        elif settings.quality == "SUPER":
            denoiser_type = high_denoiser_node

        sid_super_group.links.new(
            denoiser_type.outputs['Denoised Diffuse'],
            output_node.inputs['DN Diffuse']
            )
        sid_super_group.links.new(
            denoiser_type.outputs['Denoised Reflection'],
            output_node.inputs['DN Reflection']
            )
        if settings.use_refraction:
            sid_super_group.links.new(
                denoiser_type.outputs['Denoised Refraction'],
                output_node.inputs['DN Refraction']
            )
        if settings.use_transmission:
            sid_super_group.links.new(
                denoiser_type.outputs['Denoised Transmission'],
                output_node.inputs['DN Transmission']
            )
        if settings.use_sss:
            sid_super_group.links.new(
                denoiser_type.outputs['Denoised SSS'],
                output_node.inputs['DN SSS']
            )
        if settings.use_emission:
            sid_super_group.links.new(
                denoiser_type.outputs['Denoised Emission'],
                output_node.inputs['Emission']
            )

        if settings.use_volumetric:
            sid_super_group.links.new(
                denoiser_type.outputs['Denoised Volume'],
                output_node.inputs['DN Volume']
            )
            sid_super_group.links.new(
                denoiser_type.outputs['Denoised VolumeEmission'],
                output_node.inputs['DN VolumeEmission']
            )

        sid_super_group.links.new(
            denoiser_type.outputs['Bad Pass'],
            output_node.inputs['Bad Pass']
        )
    return sid_super_group