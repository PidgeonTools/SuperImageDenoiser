import bpy

from .. import SID_Settings

def create_luxcore_passes(
        settings: SID_Settings,
        context,
        renlayers_node,
        sid_node,
        view_layer,
        output_file_node,
        composite_node,
        ):
    
    scene = context.scene
    ntree = scene.node_tree
    ##Enable Passes##
    view_layer.luxcore.aovs.avg_shading_normal = True
    view_layer.luxcore.aovs.albedo = True
    # Diffuse
    view_layer.luxcore.aovs.direct_diffuse = True
    view_layer.luxcore.aovs.indirect_diffuse = True
    # Glossy
    view_layer.luxcore.aovs.direct_glossy = True
    view_layer.luxcore.aovs.indirect_glossy = True
    # Specular
    view_layer.luxcore.aovs.indirect_specular = True
    # Volume
    # no specific volume pass
    # Emission & Environment
    view_layer.luxcore.aovs.emission = True
    # Connect it all for LuxCore
    renlayers_node.layer = view_layer.name

    ntree.links.new(
        renlayers_node.outputs["DIRECT_DIFFUSE"],
        sid_node.inputs["DiffDir"]
        )
    ntree.links.new(
        renlayers_node.outputs["INDIRECT_DIFFUSE"],
        sid_node.inputs["DiffInd"]
        )
    ntree.links.new(
        renlayers_node.outputs["DIRECT_GLOSSY"],
        sid_node.inputs["GlossDir"]
        )
    ntree.links.new(
        renlayers_node.outputs["INDIRECT_GLOSSY"],
        sid_node.inputs["GlossInd"]
        )

    if settings.use_transmission:
        ntree.links.new(
            renlayers_node.outputs["INDIRECT_SPECULAR"],
            sid_node.inputs["TransDir"]
            )

    if settings.use_emission:
        ntree.links.new(
            renlayers_node.outputs["EMISSION"],
            sid_node.inputs["Emit"]
            )
    ntree.links.new(
        renlayers_node.outputs["Alpha"],
        sid_node.inputs["Alpha"]
        )
    ntree.links.new(
        renlayers_node.outputs["Image"],
        sid_node.inputs["Noisy Image"]
        )
    ntree.links.new(
        renlayers_node.outputs["ALBEDO"],
        sid_node.inputs["Denoising Albedo"]
        )
    ntree.links.new(
        renlayers_node.outputs["AVG_SHADING_NORMAL"],
        sid_node.inputs["Denoising Normal"]
        )


    if settings.use_mlEXR:
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

        if settings.use_emission:
            output_file_node.file_slots.new("Emission")
            ntree.links.new(
                sid_node.outputs['Emission'],
                output_file_node.inputs['Emission']
                )

        if settings.use_caustics:
            output_file_node.file_slots.new("Caustics")
            ntree.links.new(
                sid_node.outputs['DN Caustics'],
                output_file_node.inputs['Caustics']
                )

        output_file_node.format.file_format = 'OPEN_EXR_MULTILAYER'
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
    return sid_node