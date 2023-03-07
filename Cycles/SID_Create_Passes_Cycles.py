import bpy
from bpy.types import Context, Node, NodeSocket, ViewLayer
from typing import List

from .. import SID_Settings

def create_cycles_passes(
        settings: SID_Settings,
        context: Context,
        renlayers_node: Node,
        sid_node: Node,
        view_layer: ViewLayer,
        output_file_node: Node,
        connect_sockets: List[NodeSocket],
        temporal_output_file_node: Node
        ):

    scene = context.scene
    ntree = scene.node_tree

    # Turn off built-in OpenImageDenoiser
    if hasattr(scene.cycles, 'use_denoising'):
        scene.cycles.use_denoising = False

    ##Enable Passes##
    # Denoising Normal, Denoising Albedo
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
    # Temporal
    if settings.denoiser_type == "SID TEMPORAL":
        view_layer.use_motion_blur = False
        view_layer.use_pass_vector = True

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

    if not "Noisy Image" in renlayers_node.outputs or not renlayers_node.outputs["Noisy Image"].enabled:
        ntree.links.new(
            renlayers_node.outputs["Image"],
            sid_node.inputs["Noisy Image"]
            )
    else:
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
                sid_node.outputs['Environment'],
                output_file_node.inputs['Env']
                )
    if settings.denoiser_type == "SID TEMPORAL":
        ntree.links.new(
            sid_output_socket,
            temporal_output_file_node.inputs["Image"]
            )
        
        temporal_output_file_node.file_slots.new("Vector")
        ntree.links.new(
            renlayers_node.outputs["Vector"],
            temporal_output_file_node.inputs["Vector"]
            )
        
        temporal_output_file_node.file_slots.new("Depth")
        ntree.links.new(
            renlayers_node.outputs["Depth"],
            temporal_output_file_node.inputs["Depth"]
            )
        settings.inputdir = bpy.path.abspath(settings.inputdir)
        temporal_output_file_node.base_path = settings.inputdir + "noisy/######" 
