import bpy
from bpy.types import Context, Node, NodeSocket, ViewLayer
from typing import List

from .. import SID_Settings

def create_luxcore_passes(
        settings: SID_Settings,
        context: Context,
        renlayers_node: Node,
        sid_node: Node,
        view_layer: ViewLayer,
        output_file_node: Node,
        connect_sockets: List[NodeSocket],
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


    sid_output_socket: NodeSocket
    if settings.quality == 'SUPER':
        sid_output_socket = sid_node.outputs["SUPER Quality"]
    elif settings.quality == 'HIGH':
        sid_output_socket = sid_node.outputs["High Quality"]
    else:
        sid_output_socket = sid_node.outputs["Standard Quality"]

    # Connect SID Node to sockets
    for socket in connect_sockets:
        ntree.links.new(sid_output_socket, socket)

    if settings.use_mlEXR:
        ntree.links.new(
            sid_output_socket,
            output_file_node.inputs["Image"]
            )

        output_file_node.file_slots.new("Diffuse")
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
