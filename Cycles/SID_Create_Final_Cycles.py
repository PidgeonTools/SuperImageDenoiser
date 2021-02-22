import bpy

from .. import SID_Settings

def create_cycles_final(
        settings: SID_Settings,
        context,
        renlayers_node,
        sid_node,
        view_layer
        ):

    scene = context.scene
    ntree = scene.node_tree
    viewlayer_displace = 0

    ##Enable Passes##
    view_layer.cycles.denoising_store_passes = True
    # Diffuse
    view_layer.use_pass_diffuse_direct = True
    view_layer.use_pass_diffuse_indirect = True
    view_layer.use_pass_diffuse_color = True
    # Glossy
    view_layer.use_pass_glossy_direct = True
    view_layer.use_pass_glossy_indirect = True
    view_layer.use_pass_glossy_color = True
    # Transmission
    view_layer.use_pass_transmission_direct = settings.use_transmission
    view_layer.use_pass_transmission_indirect = settings.use_transmission
    view_layer.use_pass_transmission_color = settings.use_transmission
    # Volume
    view_layer.cycles.use_pass_volume_direct = settings.use_volumetric
    view_layer.cycles.use_pass_volume_indirect = settings.use_volumetric
    # Emission & Environment
    view_layer.use_pass_emit = settings.use_emission
    view_layer.use_pass_environment = settings.use_environment

    # Connect it all for Cycles
    ntree.links.new(
        renlayers_node.outputs["DiffDir"],
        sid_node.inputs["DiffDir"]
        )
    ntree.links.new(
        renlayers_node.outputs["DiffInd"],
        sid_node.inputs["DiffInd"]
        )
    ntree.links.new(
        renlayers_node.outputs["DiffCol"],
        sid_node.inputs["DiffCol"]
        )
    ntree.links.new(
        renlayers_node.outputs["GlossDir"],
        sid_node.inputs["GlossDir"]
        )
    ntree.links.new(
        renlayers_node.outputs["GlossInd"],
        sid_node.inputs["GlossInd"]
        )
    ntree.links.new(
        renlayers_node.outputs["GlossCol"],
        sid_node.inputs["GlossCol"]
        )

    if settings.use_transmission:
        ntree.links.new(
            renlayers_node.outputs["TransDir"],
            sid_node.inputs["TransDir"]
            )
        ntree.links.new(
            renlayers_node.outputs["TransInd"],
            sid_node.inputs["TransInd"]
            )
        ntree.links.new(
            renlayers_node.outputs["TransCol"],
            sid_node.inputs["TransCol"]
            )

    if settings.use_volumetric:
        ntree.links.new(
            renlayers_node.outputs["VolumeDir"],
            sid_node.inputs["VolumeDir"]
            )
        ntree.links.new(
            renlayers_node.outputs["VolumeInd"],
            sid_node.inputs["VolumeInd"]
            )

    if settings.use_emission:
        ntree.links.new(
            renlayers_node.outputs["Emit"],
            sid_node.inputs["Emit"]
            )

    if settings.use_environment:
        ntree.links.new(
            renlayers_node.outputs["Env"],
            sid_node.inputs["Env"]
            )

    ntree.links.new(
        renlayers_node.outputs["Alpha"],
        sid_node.inputs["Alpha"]
        )
    ntree.links.new(
        renlayers_node.outputs["Noisy Image"],
        sid_node.inputs["Noisy Image"]
        )
    ntree.links.new(
        renlayers_node.outputs["Denoising Albedo"],
        sid_node.inputs["Denoising Albedo"]
        )
    ntree.links.new(
        renlayers_node.outputs["Denoising Normal"],
        sid_node.inputs["Denoising Normal"]
        )


    if settings.use_mlEXR:
        output_file_node = ntree.nodes.new(type="CompositorNodeOutputFile")
        output_file_node.location = (400, viewlayer_displace - 200)
        output_file_node.file_slots.new("Diffuse")

        if settings.quality == 'SUPER':
            ntree.links.new(
                sid_node.outputs["SUPER Quality"],
                output_file_node.inputs["Image"]
                )
        elif settings.quality == 'HIGH':
            ntree.links.new(
                sid_node.outputs["High Quality"],
                output_file_node.inputs["Image"]
                )

        ntree.links.new(
            sid_node.outputs['DN Diffuse'],
            output_file_node.inputs['Diffuse']
            )

        output_file_node.file_slots.new("Glossy")
        ntree.links.new(
            sid_node.outputs['DN Glossy'],
            output_file_node.inputs['Glossy']
            )

        if settings.use_transmission:
            output_file_node.file_slots.new("Transmission")
            ntree.links.new(
                sid_node.outputs['DN Transmission'],
                output_file_node.inputs['Transmission']
                )

        if settings.use_volumetric:
            output_file_node.file_slots.new("Volume")
            ntree.links.new(
                sid_node.outputs['DN Volume'],
                output_file_node.inputs['Volume']
                )

        if settings.use_emission:
            output_file_node.file_slots.new("Emission")
            ntree.links.new(
                sid_node.outputs['Emission'],
                output_file_node.inputs['Emission']
                )
        if settings.use_environment:
            output_file_node.file_slots.new("Env")
            ntree.links.new(
                sid_node.outputs['Envrionment'],
                output_file_node.inputs['Env']
                )

        output_file_node.format.file_format = 'OPEN_EXR_MULTILAYER'
        #made me cry
    composite_node = ntree.nodes.new(type='CompositorNodeComposite')
    composite_node.location = (400, viewlayer_displace)
    if settings.quality == 'SUPER':
        ntree.links.new(
            sid_node.outputs["SUPER Quality"],
            composite_node.inputs["Image"]
            )
    elif settings.quality == 'HIGH':
        ntree.links.new(
            sid_node.outputs["High Quality"],
            composite_node.inputs["Image"]
            )
    else:
        ntree.links.new(
            sid_node.outputs["Standard Quality"],
            composite_node.inputs["Image"]
            )
    viewlayer_displace -= 1000

    return
