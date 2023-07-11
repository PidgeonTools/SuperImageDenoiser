import bpy
import os
from bpy.types import Context, Node, NodeSocket, ViewLayer
from typing import List

from .. import SID_Settings

def create_cycles_passes(
        settings: SID_Settings,
        context: Context,
        render_layer_node: Node,
        sid_node: Node,
        view_layer: ViewLayer,
        output_file_node: Node,
        connect_sockets: List[NodeSocket],
        view_layer_id: int
        ):

    scene = context.scene
    ntree = scene.node_tree
    scene.use_nodes = True

    # Turn off built-in Denoiser
    scene.cycles.use_denoising = False

    ##Enable Passes##
    # Denoising Normal, Denoising Albedo, Depth
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
        scene.render.use_motion_blur = False
        view_layer.use_pass_vector = True

    ## Connect it all for Cycles
    # Diffuse
    ntree.links.new(render_layer_node.outputs["DiffDir"],sid_node.inputs["DiffDir"])
    ntree.links.new(render_layer_node.outputs["DiffInd"],sid_node.inputs["DiffInd"])
    ntree.links.new(render_layer_node.outputs["DiffCol"],sid_node.inputs["DiffCol"])
    # Glossy
    ntree.links.new(render_layer_node.outputs["GlossDir"],sid_node.inputs["GlossDir"])
    ntree.links.new(render_layer_node.outputs["GlossInd"],sid_node.inputs["GlossInd"])
    ntree.links.new(render_layer_node.outputs["GlossCol"],sid_node.inputs["GlossCol"])
    # Transmission
    if settings.use_transmission:
        ntree.links.new(render_layer_node.outputs["TransDir"],sid_node.inputs["TransDir"])
        ntree.links.new(render_layer_node.outputs["TransInd"],sid_node.inputs["TransInd"])
        ntree.links.new(render_layer_node.outputs["TransCol"],sid_node.inputs["TransCol"])
    # Volume
    if settings.use_volumetric:
        ntree.links.new(render_layer_node.outputs["VolumeDir"],sid_node.inputs["VolumeDir"])
        ntree.links.new(render_layer_node.outputs["VolumeInd"],sid_node.inputs["VolumeInd"])
    # Emission
    if settings.use_emission:
        ntree.links.new(render_layer_node.outputs["Emit"],sid_node.inputs["Emit"])
    # Environment
    if settings.use_environment:
        ntree.links.new(render_layer_node.outputs["Env"],sid_node.inputs["Env"])
    # Alpha
    ntree.links.new(render_layer_node.outputs["Alpha"],sid_node.inputs["Alpha"])

    if not "Noisy Image" in render_layer_node.outputs or not render_layer_node.outputs["Noisy Image"].enabled:
        ntree.links.new(render_layer_node.outputs["Image"],sid_node.inputs["Noisy Image"])
    else:
        ntree.links.new(render_layer_node.outputs["Noisy Image"],sid_node.inputs["Noisy Image"])

    ntree.links.new(render_layer_node.outputs["Denoising Albedo"],sid_node.inputs["Denoising Albedo"])
    ntree.links.new(render_layer_node.outputs["Denoising Normal"],sid_node.inputs["Denoising Normal"])

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

    # Connect SID Node to mlEXR node
    if settings.SID_mlEXR:
        # Image
        ntree.links.new(sid_output_socket,output_file_node.inputs["Image"])
        # Diffuse
        output_file_node.file_slots.new("Diffuse")
        ntree.links.new(sid_node.outputs['DN Diffuse'],output_file_node.inputs['Diffuse'])
        # Glossy
        output_file_node.file_slots.new("Glossy")
        ntree.links.new(sid_node.outputs['DN Glossy'],output_file_node.inputs['Glossy'])
        # Transmission
        if settings.use_transmission:
            output_file_node.file_slots.new("Transmission")
            ntree.links.new(sid_node.outputs['DN Transmission'],output_file_node.inputs['Transmission'])
        # Volume
        if settings.use_volumetric:
            output_file_node.file_slots.new("Volume")
            ntree.links.new(sid_node.outputs['DN Volume'],output_file_node.inputs['Volume'])
        # Emission
        if settings.use_emission:
            output_file_node.file_slots.new("Emission")
            ntree.links.new(sid_node.outputs['Emission'],output_file_node.inputs['Emission'])
        # Environment
        if settings.use_environment:
            output_file_node.file_slots.new("Env")
            ntree.links.new(sid_node.outputs['Env'],output_file_node.inputs['Env'])

    # Connect RenderLayer to mlEXR node
    if settings.denoiser_type == "SID TEMPORAL":
        # Image
        ntree.links.new(sid_output_socket,output_file_node.inputs["Image"])
        # Vector
        output_file_node.file_slots.new("Vector")
        ntree.links.new(render_layer_node.outputs["Vector"],output_file_node.inputs["Vector"])
        # Depth
        output_file_node.file_slots.new("Depth")
        ntree.links.new(render_layer_node.outputs["Denoising Depth"],output_file_node.inputs["Depth"])
        # Temporal Albedo
        output_file_node.file_slots.new("Temporal Albedo")
        ntree.links.new(sid_node.outputs["Temporal Albedo"],output_file_node.inputs["Temporal Albedo"])
        
        # Set output path
        settings.inputdir = bpy.path.abspath(settings.inputdir)
        output_file_node.base_path = os.path.join(settings.inputdir,"noisy",f"{view_layer_id}","######") 
