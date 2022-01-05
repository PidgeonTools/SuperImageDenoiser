import bpy
from bpy.types import Context, Node, NodeSocket, ViewLayer
from typing import List

from .. import SID_Settings

def create_renderman_passes(
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

    #Important
    view_layer.use_pass_normal = True
    # Diffuse
    view_layer.use_pass_diffuse_direct = True
    view_layer.use_pass_diffuse_indirect = True
    view_layer.use_pass_diffuse_color = True
    # Reflection
    view_layer.use_pass_glossy_direct = True
    view_layer.use_pass_glossy_indirect = True
    # SSS
    view_layer.use_pass_subsurface_indirect = settings.use_sss
    # Emission
    view_layer.use_pass_emit = settings.use_emission

    # Connect it all for Renderman
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
        sid_node.inputs["Denoising Albedo"]
        )

    ntree.links.new(
        renlayers_node.outputs["GlossDir"],
        sid_node.inputs["GlossDir"]
        )

    ntree.links.new(
        renlayers_node.outputs["GlossInd"],
        sid_node.inputs["GlossInd"]
        )

    if settings.use_sss:
        ntree.links.new(
            renlayers_node.outputs["SubsurfaceInd"],
            sid_node.inputs["SubsurfaceInd"]
            )

    if settings.use_emission:
        ntree.links.new(
            renlayers_node.outputs["Emit"],
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
        renlayers_node.outputs["Normal"],
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

        output_file_node.file_slots.new("Gloss")
        ntree.links.new(
            sid_node.outputs['DN Glossy'],
            output_file_node.inputs['Gloss']
            )

        if settings.use_sss:
            output_file_node.file_slots.new("SubsurfaceInd")
            ntree.links.new(
                sid_node.outputs['DN Subsurface'],
                output_file_node.inputs['SubsurfaceInd']
                )

        if settings.use_emission:
            output_file_node.file_slots.new("Emission")
            ntree.links.new(
                sid_node.outputs['Emission'],
                output_file_node.inputs['Emission']
                )