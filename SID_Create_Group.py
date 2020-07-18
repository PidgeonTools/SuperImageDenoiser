import bpy

from . import SID_Settings

def create_sid_super_group(
        standard_denoiser_tree,
        high_denoiser_tree,
        super_denoiser_tree,
        settings: SID_Settings
        ):

    RenderEngine = bpy.context.scene.render.engine

    ##############
    ### CYCLES ###
    ##############
    if RenderEngine == 'CYCLES':
        sid_super_group = bpy.data.node_groups.new(
            type='CompositorNodeTree',
            name=".SuperImageDenoiser.SuperGroup"
            )
        input_node = sid_super_group.nodes.new("NodeGroupInput")
        input_node.location = (-200, 0)

        output_node = sid_super_group.nodes.new("NodeGroupOutput")
        output_node.location = (1800, 0)

        sid_super_group.inputs.new("NodeSocketColor", "Noisy Image")
        sid_super_group.inputs.new("NodeSocketVector", "Denoising Normal")
        sid_super_group.inputs.new("NodeSocketColor", "Denoising Albedo")
        sid_super_group.inputs.new("NodeSocketColor", "Alpha")
        sid_super_group.inputs.new("NodeSocketColor", "DiffDir")
        sid_super_group.inputs.new("NodeSocketColor", "DiffInd")
        sid_super_group.inputs.new("NodeSocketColor", "DiffCol")
        sid_super_group.inputs.new("NodeSocketColor", "GlossDir")
        sid_super_group.inputs.new("NodeSocketColor", "GlossInd")
        sid_super_group.inputs.new("NodeSocketColor", "GlossCol")
        if settings.use_transmission:
            sid_super_group.inputs.new("NodeSocketColor", "TransDir")
            sid_super_group.inputs.new("NodeSocketColor", "TransInd")
            sid_super_group.inputs.new("NodeSocketColor", "TransCol")
        if settings.use_volumetric:
            sid_super_group.inputs.new("NodeSocketColor", "VolumeDir")
            sid_super_group.inputs.new("NodeSocketColor", "VolumeInd")
        if settings.use_emission:
            sid_super_group.inputs.new("NodeSocketColor", "Emit")
        if settings.use_environment:
            sid_super_group.inputs.new("NodeSocketColor", "Env")

        sid_super_group.outputs.new("NodeSocketColor", "Standard Quality")
        sid_super_group.outputs.new("NodeSocketColor", "High Quality")
        sid_super_group.outputs.new("NodeSocketColor", "SUPER Quality")


        if settings.use_mlEXR:
            sid_super_group.outputs.new("NodeSocketColor", "DN Diffuse")
            sid_super_group.outputs.new("NodeSocketColor", 'DN Glossy')
            if settings.use_transmission:
                sid_super_group.outputs.new("NodeSocketColor", 'DN Transmission')
            if settings.use_volumetric:
                sid_super_group.outputs.new("NodeSocketColor", 'DN Volume')
            if settings.use_emission:
                sid_super_group.outputs.new("NodeSocketColor", 'Emission')
            if settings.use_environment:
                sid_super_group.outputs.new("NodeSocketColor", "Envrionment")



        standard_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
        standard_denoiser_node.node_tree = standard_denoiser_tree
        standard_denoiser_node.location = (0, 900)
        standard_denoiser_node.name = standard_denoiser_node.label = "Standard Denoiser"

        high_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
        high_denoiser_node.node_tree = high_denoiser_tree
        high_denoiser_node.location = (0, 600)
        high_denoiser_node.name = high_denoiser_node.label = "High Quality Denoiser"

        super_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
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
            sid_super_group.links.new(
                input_node.outputs[input],
                standard_denoiser_node.inputs[input]
                )

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
            sid_super_group.links.new(
                input_node.outputs[input],
                super_denoiser_node.inputs[input]
                )
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
        sid_super_group.links.new(
            super_denoiser_node.outputs['Denoised Image'],
            output_node.inputs['SUPER Quality']
            )

        if settings.use_mlEXR and settings.quality != 'STANDARD':

            if settings.quality == "HIGH":
                denoiser_type = high_denoiser_node
            elif settings.quality == "SUPER":
                denoiser_type = super_denoiser_node

            sid_super_group.links.new(
                denoiser_type.outputs['Denoised Diffuse'],
                output_node.inputs['DN Diffuse']
                )
            sid_super_group.links.new(
                denoiser_type.outputs['Denoised Glossy'],
                output_node.inputs['DN Glossy']
                )

            if settings.use_transmission:
                sid_super_group.links.new(
                    denoiser_type.outputs['Denoised Transmission'],
                    output_node.inputs['DN Transmission']
                )
            if settings.use_volumetric:
                sid_super_group.links.new(
                    denoiser_type.outputs['Denoised Volume'],
                    output_node.inputs['DN Volume']
                )
            if settings.use_emission:
                sid_super_group.links.new(
                    denoiser_type.outputs['Emission'],
                    output_node.inputs['Emission']
                )
            if settings.use_environment:
                sid_super_group.links.new(
                    denoiser_type.outputs["Envrionment"],
                    output_node.inputs["Envrionment"]
                )

    ###############
    ### LUXCORE ###
    ###############

    if RenderEngine == 'LUXCORE':
        sid_super_group = bpy.data.node_groups.new(
            type='CompositorNodeTree',
            name=".SuperImageDenoiser.SuperGroup"
            )
        input_node = sid_super_group.nodes.new("NodeGroupInput")
        input_node.location = (-200, 0)

        output_node = sid_super_group.nodes.new("NodeGroupOutput")
        output_node.location = (1800, 0)

        sid_super_group.inputs.new("NodeSocketColor", "Noisy Image")
        sid_super_group.inputs.new("NodeSocketVector", "Denoising Normal")
        sid_super_group.inputs.new("NodeSocketColor", "Denoising Albedo")
        sid_super_group.inputs.new("NodeSocketColor", "Alpha")
        sid_super_group.inputs.new("NodeSocketColor", "DiffDir")
        sid_super_group.inputs.new("NodeSocketColor", "DiffInd")
        sid_super_group.inputs.new("NodeSocketColor", "GlossDir")
        sid_super_group.inputs.new("NodeSocketColor", "GlossInd")
        if settings.use_transmission:
            sid_super_group.inputs.new("NodeSocketColor", "TransInd")
        if settings.use_emission:
            sid_super_group.inputs.new("NodeSocketColor", "Emit")

        sid_super_group.outputs.new("NodeSocketColor", "Standard Quality")
        sid_super_group.outputs.new("NodeSocketColor", "High Quality")
        sid_super_group.outputs.new("NodeSocketColor", "SUPER Quality")


        if settings.use_mlEXR:
            sid_super_group.outputs.new("NodeSocketColor", "DN Diffuse")
            sid_super_group.outputs.new("NodeSocketColor", 'DN Glossy')
            if settings.use_transmission:
                sid_super_group.outputs.new("NodeSocketColor", 'DN Transmission')
            if settings.use_emission:
                sid_super_group.outputs.new("NodeSocketColor", 'Emission')



        standard_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
        standard_denoiser_node.node_tree = standard_denoiser_tree
        standard_denoiser_node.location = (0, 900)
        standard_denoiser_node.name = standard_denoiser_node.label = "Standard Denoiser"

        high_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
        high_denoiser_node.node_tree = high_denoiser_tree
        high_denoiser_node.location = (0, 600)
        high_denoiser_node.name = high_denoiser_node.label = "High Quality Denoiser"

        super_denoiser_node = sid_super_group.nodes.new("CompositorNodeGroup")
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
            sid_super_group.links.new(
                input_node.outputs[input],
                standard_denoiser_node.inputs[input]
                )

        # High & SUPER
        input_sockets = [
            "Noisy Image",
            "Denoising Normal",
            "Denoising Albedo",
            "Alpha",
            "DiffDir",
            "DiffInd",
            "GlossDir",
            "GlossInd",
        ]
        if settings.use_transmission:
            input_sockets.extend([
                "TransInd",
            ])
        if settings.use_emission:
            input_sockets.extend([
                "Emit",
            ])


        for input in input_sockets:
            sid_super_group.links.new(
                input_node.outputs[input],
                super_denoiser_node.inputs[input]
                )
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
        sid_super_group.links.new(
            super_denoiser_node.outputs['Denoised Image'],
            output_node.inputs['SUPER Quality']
            )

        if settings.use_mlEXR and settings.quality != 'STANDARD':

            if settings.quality == "HIGH":
                denoiser_type = high_denoiser_node
            elif settings.quality == "SUPER":
                denoiser_type = super_denoiser_node

            sid_super_group.links.new(
                denoiser_type.outputs['Denoised Diffuse'],
                output_node.inputs['DN Diffuse']
                )
            sid_super_group.links.new(
                denoiser_type.outputs['Denoised Glossy'],
                output_node.inputs['DN Glossy']
                )
            if settings.use_transmission:
                sid_super_group.links.new(
                    denoiser_type.outputs['Denoised Transmission'],
                    output_node.inputs['DN Transmission']
                )
            if settings.use_emission:
                sid_super_group.links.new(
                    denoiser_type.outputs['Emission'],
                    output_node.inputs['Emission']
                )

    return sid_super_group
