import bpy
from bpy.types import Context, Node, NodeSocket, ViewLayer
from typing import List

from .. import SID_Settings

def create_octane_passes(
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
    view_layer.use_pass_oct_info_shading_normal = True
    # Diffuse
    view_layer.use_pass_oct_diff = True
    view_layer.use_pass_oct_diff_filter = True
    # Reflection
    view_layer.use_pass_oct_reflect = True
    # Refraction
    view_layer.use_pass_oct_refract = settings.use_refraction
    # Transmission
    view_layer.use_pass_oct_transm = settings.use_transmission
    # SSS
    view_layer.use_pass_oct_sss = settings.use_sss
    # Volume
    view_layer.use_pass_oct_volume = settings.use_volumetric
    view_layer.use_pass_oct_vol_emission = settings.use_volumetric
    # Emission
    view_layer.use_pass_oct_emitters = settings.use_emission

    # Connect it all for Octane
    ntree.links.new(
        renlayers_node.outputs["OctDiff"],
        sid_node.inputs["Diffuse"]
        )
    ntree.links.new(
        renlayers_node.outputs["OctDiffFilter"],
        sid_node.inputs["Denoising Albedo"]
        )
    ntree.links.new(
        renlayers_node.outputs["OctReflect"],
        sid_node.inputs["Reflection"]
        )

    if settings.use_transmission:
        ntree.links.new(
            renlayers_node.outputs["OctTransm"],
            sid_node.inputs["Transmission"]
            )

    if settings.use_refraction:
        ntree.links.new(
            renlayers_node.outputs["OctRefract"],
            sid_node.inputs["Refraction"]
            )

    if settings.use_sss:
        ntree.links.new(
            renlayers_node.outputs["OctSSS"],
            sid_node.inputs["SSS"]
            )

    if settings.use_volumetric:
        ntree.links.new(
            renlayers_node.outputs["OctVolume"],
            sid_node.inputs["Volume"]
            )
        ntree.links.new(
            renlayers_node.outputs["OctVolEmission"],
            sid_node.inputs["VolumeEmission"]
            )

    if settings.use_emission:
        ntree.links.new(
            renlayers_node.outputs["OctEmitters"],
            sid_node.inputs["Emission"]
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
        renlayers_node.outputs["OctShadingNormal"],
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

        output_file_node.file_slots.new("Reflection")
        ntree.links.new(
            sid_node.outputs['DN Reflection'],
            output_file_node.inputs['Reflection']
            )

        if settings.use_refraction:
            output_file_node.file_slots.new("Refraction")
            ntree.links.new(
                sid_node.outputs['DN Refraction'],
                output_file_node.inputs['Refraction']
                )

        if settings.use_transmission:
            output_file_node.file_slots.new("Transmission")
            ntree.links.new(
                sid_node.outputs['DN Transmission'],
                output_file_node.inputs['Transmission']
                )

        if settings.use_sss:
            output_file_node.file_slots.new("SSS")
            ntree.links.new(
                sid_node.outputs['DN SSS'],
                output_file_node.inputs['SSS']
                )

        if settings.use_emission:
            output_file_node.file_slots.new("Emission")
            ntree.links.new(
                sid_node.outputs['Emission'],
                output_file_node.inputs['Emission']
                )

        if settings.use_volumetric:
            output_file_node.file_slots.new("Volume")
            ntree.links.new(
                sid_node.outputs['DN Volume'],
                output_file_node.inputs['Volume']
                )

            output_file_node.file_slots.new("VolumeEmission")
            ntree.links.new(
                sid_node.outputs['DN VolumeEmission'],
                output_file_node.inputs['VolumeEmission']
                )

        output_file_node.file_slots.new("Bad Pass")
        ntree.links.new(
            sid_node.outputs['Bad Pass'],
            output_file_node.inputs['Bad Pass']
            )
