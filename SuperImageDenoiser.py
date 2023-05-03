import bpy, os
from bpy.types import Context, Node, NodeLink, NodeSocket, Operator, ViewLayer, Timer, Scene
from typing import Callable, List

from .SID_Create_DenoiserGroup import create_sid_super_denoiser_group
from .SID_Create_Group import create_sid_group
from .SID_QualityStandart import create_sid_denoiser_standard

from .Cycles.SID_QualityHigh_Cycles import create_sid_denoiser_high_cy
from .Cycles.SID_QualitySuper_Cycles import create_sid_denoiser_super_cy
from .Cycles.SID_Create_Passes_Cycles import create_cycles_passes

from .Temporal.SID_Create_Temporal_Groups import create_temporal_setup

from . import SID_Settings

def find_node(start_node: Node, predicate: Callable[[Node], bool], recursive: bool = False) -> Node:
    '''
    Finds the first Node attached to start_node that matches a predicate condition.
    If recursive is True, this function will recursively search via all linked Output sockets.
    '''
    link: NodeLink
    for output in start_node.outputs:
        for link in output.links:
            if not link.is_valid:
                continue

            if predicate(link.to_node):
                return link.to_node

            if recursive:
                node = find_node(link.to_node, predicate, recursive)
                if node:
                    return node
    return None

def is_sid_group(node: Node) -> bool:
    ''' Predicate that returns True if node is a SuperImageDenoiser '''
    return (
        node.bl_idname == 'CompositorNodeGroup'
        and node.name.startswith(("sid_node", ".SuperImageDenoiser"))
        )

def is_composite_output(node: Node) -> bool:
    ''' Predicate that returns True if node is a Composite Output '''
    return node.bl_idname == 'CompositorNodeComposite'

def is_sid_mlexr_file_output(node: Node) -> bool:
    ''' Predicate that returns True if node is a SID Multi-Layer EXR File Output '''
    return (
        node.bl_idname == 'CompositorNodeOutputFile'
        and node.name.startswith("mlEXR Node")
        )

def is_optix_temporal_output(node: Node) -> bool:
    ''' Predicate that returns True if node is an OptiX Temporal Output '''
    return (
        node.bl_idname == 'CompositorNodeOutputFile'
        and node.name.startswith("OptiX Temporal Output")
        )

class SID_Create(Operator):
    bl_idname = "object.superimagedenoise"
    bl_label = "Add Super Denoiser"
    bl_description = "Enables all the necessary passes, Creates all the nodes you need, connects them all for you, to save the time you don't need to waste"

    def execute(self, context: Context):
        # Sets basic variables
        scene = context.scene
        settings: SID_Settings = scene.sid_settings
        scene.use_nodes = True
        scene.render.use_compositing = True
        ntree = scene.node_tree

        # Resets the compositor
        for comp in [node for node in ntree.nodes if (
                is_composite_output(node) or
                is_sid_mlexr_file_output(node) or
                is_sid_group(node) or
                is_optix_temporal_output(node)
            )]:
            ntree.nodes.remove(comp)

        # Create Tripple Denoiser Group
        sid_standard_tree = create_sid_denoiser_standard()
        sid_high_tree = create_sid_super_denoiser_group(create_sid_denoiser_high_cy(), settings)
        sid_super_tree = create_sid_super_denoiser_group(create_sid_denoiser_super_cy(), settings)
        sid_group = create_sid_group(sid_standard_tree,sid_high_tree,sid_super_tree,settings)

        # Create a denoiser for each View layer
        viewlayer_displace = 0
        view_layer_id = 0
        view_layer: ViewLayer
        out_node: NodeSocket
        link: NodeLink
        
        for view_layer in scene.view_layers:
            if not view_layer.use:
                continue
            view_layer_id += 1

            # Look for existing Render Layer Node
            render_layer_node: Node = next((
                node for node in ntree.nodes
                if node.bl_idname == 'CompositorNodeRLayers'
                    and node.layer == view_layer.name
                ),
                None
                )
            
            composite_node: Node = None
            sid_node: Node = None
            output_file_node: Node = None
            optix_temporal_output_file_node: Node = None

            # Sockets to connect to the SID Node
            connect_sockets: List[NodeSocket] = []

            if render_layer_node:

                ###
                #region Look for existing nodes
                ###

                # Look for any existing SID File Output node
                mlexr_output_file_node = find_node(render_layer_node, is_sid_mlexr_file_output, True)
                if mlexr_output_file_node:
                    ntree.nodes.remove(mlexr_output_file_node)
                    mlexr_output_file_node = None
                    
                # Look for any existing OptiX Temporal File Output node
                optix_temporal_output_file_node = find_node(render_layer_node, is_optix_temporal_output, True)
                if optix_temporal_output_file_node:
                    ntree.nodes.remove(optix_temporal_output_file_node)
                    optix_temporal_output_file_node = None

                # Look for existing SID Node connected to Render Layer
                sid_node = find_node(render_layer_node, is_sid_group, False)
                if sid_node:
                    # Look for a Composite Output node somewhere via the SID Node
                    composite_node = find_node(sid_node, is_composite_output, True)

                    # Reconnect every node connected to the SID Node
                    for out_node in sid_node.outputs:
                        for link in out_node.links:
                            if not link.is_valid:
                                continue
                            connect_sockets.append(link.to_socket)

                    if not composite_node:
                        composite_node = find_node(render_layer_node, is_composite_output, True)
                        if composite_node:
                            ntree.nodes.remove(composite_node)
                            composite_node = None

                else:
                    # No SID Node was found directly connected to the Render Layer.
                    # Look for one attached some other way, and delete it if found,
                    # because this is not considered valid.
                    sid_node = find_node(render_layer_node, is_sid_group, True)
                    if sid_node:
                        # Look for an attached Composite Output node, and delete it if found.
                        composite_node = find_node(sid_node, is_composite_output, True)
                        if composite_node:
                            # Delete the Composite Output node; we'll recreate it later
                            ntree.nodes.remove(composite_node)
                            composite_node = None

                        # Delete the SID Node; we'll recreate it later
                        ntree.nodes.remove(sid_node)
                        sid_node = None

                if not sid_node:
                    # Look for an attached Composite Output node. If we find one,leave it alone.
                    composite_node = find_node(render_layer_node, is_composite_output, True)
                ###    
                #endregion
                ###

                ###
                #region Check if SID is connected already.
                ###

                # Output links from "Image" socket should have a SID connected in-between
                for link in render_layer_node.outputs['Image'].links:
                    if not link.is_valid:
                        continue

                    # Ignore if for some reason it's linked to the SID node
                    if is_sid_group(link.to_node):
                        continue

                    connect_sockets.append(link.to_socket)

                ###
                #endregion
                ###

            if not render_layer_node:
                #Create Basic Nodes
                render_layer_node = ntree.nodes.new(type='CompositorNodeRLayers')

                render_layer_node.location = (-100, viewlayer_displace)
                render_layer_node.layer = view_layer.name
                render_layer_node.name = "Render Layer"

            if not sid_node:
                sid_node = ntree.nodes.new('CompositorNodeGroup')
                sid_node.location = (200, viewlayer_displace)

            sid_node.node_tree = sid_group
            sid_node.name = "sid_node"

            if not composite_node:
                composite_node = ntree.nodes.new(type='CompositorNodeComposite')
                composite_node.location = (400, viewlayer_displace)
                composite_node.name = "Output Node"

                connect_sockets.append(composite_node.inputs['Image'])

            if settings.SID_mlEXR or (settings.denoiser_type == "SID TEMPORAL"):
                output_file_node = ntree.nodes.new(type='CompositorNodeOutputFile')
                output_file_node.name = "mlEXR Node"
                output_file_node.location = (400, viewlayer_displace - 200)
                output_file_node.format.file_format = 'OPEN_EXR_MULTILAYER'

                if settings.SID_mlEXR_Compressed:
                    output_file_node.format.color_depth = '16'
                    output_file_node.format.exr_codec = 'DWAA'
                else:
                    output_file_node.format.color_depth = '32'
                    output_file_node.format.exr_codec = 'ZIP'

            create_cycles_passes(settings, context, render_layer_node, sid_node, view_layer, output_file_node, connect_sockets, view_layer_id)

            viewlayer_displace -= 1000

        return {'FINISHED'}
    