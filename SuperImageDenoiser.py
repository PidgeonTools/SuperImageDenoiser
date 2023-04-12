import bpy, os
from bpy.types import Context, Node, NodeLink, NodeSocket, Operator, ViewLayer, Timer, Scene
from typing import Callable, List

from .SID_Create_DenoiserGroup import create_sid_super_denoiser_group
from .SID_Create_Group import create_sid_super_group
from .SID_QualityStandart import create_sid_denoiser_standard

from .Cycles.SID_QualityHigh_Cycles import create_sid_denoiser_high_cy
from .Cycles.SID_QualitySuper_Cycles import create_sid_denoiser_super_cy
from .Cycles.SID_Create_Passes_Cycles import create_cycles_passes

from .LuxCore.SID_QualityHigh_LuxCore import create_sid_denoiser_high_lc
from .LuxCore.SID_QualitySuper_LuxCore import create_sid_denoiser_super_lc
from .LuxCore.SID_Create_Passes_LuxCore import create_luxcore_passes

from .Octane.SID_QualityHigh_Octane import create_sid_denoiser_high_oc
from .Octane.SID_Create_Passes_Octane import create_octane_passes

from .Renderman.SID_QualityHigh_Renderman import create_sid_denoiser_high_rm
from .Renderman.SID_QualitySuper_Renderman import create_sid_denoiser_super_rm
from .Renderman.SID_Create_Passes_Renderman import create_renderman_passes

from .Temporal.SID_Create_Temporal_Groups import create_temporal_setup

from . import SID_Settings

def find_node(start_node: Node, predicate: Callable[[Node], bool], recursive: bool = False) -> Node:
    '''
    Finds the first Node attached to start_node that matches a predicate condition.
    If recursive is True, this function will recursively search via all linked Output sockets.
    '''

    # Search all Outputs of provided starting Node
    for output in start_node.outputs:
        # Search all Nodes linked to this Output socket
        link: NodeLink
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
def is_sid_super_group(node: Node) -> bool:
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
def is_sid_temporal_output(node: Node) -> bool:
    ''' Predicate that returns True if node is a SID Temporal Output '''
    return (
        node.bl_idname == 'CompositorNodeOutputFile'
        and node.name.startswith("Temporal Output")
        )

class SID_Create(Operator):
    bl_idname = "object.superimagedenoise"
    bl_label = "Add Super Denoiser"
    bl_description = "Enables all the necessary passes, Creates all the nodes you need, connects them all for you, to save the time you don't need to waste"

    def execute(self, context: Context):
    
        scene = context.scene
        RenderEngine = scene.render.engine
        settings: SID_Settings = scene.sid_settings

        # Initialise important settings
        # if scene.render.engine is not 'CYCLES' or not 'LUXCORE':
        #     scene.render.engine = 'CYCLES'
        scene.use_nodes = True
        scene.render.use_compositing = True


        ntree = scene.node_tree

        if not settings.compositor_reset:
            # Clear Compositor Output
            for comp in [node for node in ntree.nodes if (
                    is_composite_output(node) or
                    is_sid_mlexr_file_output(node) or
                    is_sid_super_group(node) or
                    is_sid_temporal_output(node)
                )]:
                ntree.nodes.remove(comp)


        # SID

        # Create dual denoiser node group
        sid_standard_tree = create_sid_denoiser_standard()

        if RenderEngine == 'CYCLES':
            sid_high_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_high_cy(),
                settings
                )
        elif RenderEngine == 'LUXCORE':
            sid_high_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_high_lc(),
                settings
                )
        elif RenderEngine == 'octane':
            sid_high_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_high_oc(),
                settings
                )
        elif RenderEngine == 'PRMAN_RENDER':
            sid_high_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_high_rm(),
                settings
                )
        else:
            sid_high_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_high_cy(),
                settings
                )

        if RenderEngine == 'CYCLES':
            sid_super_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_super_cy(),
                settings
                )
        elif RenderEngine == 'LUXCORE':
            sid_super_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_super_lc(),
                settings
                )
        elif RenderEngine == 'octane':
            sid_super_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_high_oc(),
                settings
                )
        if RenderEngine == 'PRMAN_RENDER':
            sid_super_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_super_rm(),
                settings
                )
        else:
            sid_super_tree = create_sid_super_denoiser_group(
                create_sid_denoiser_super_cy(),
                settings
                )

        sid_super_group = create_sid_super_group(
            sid_standard_tree,
            sid_high_tree,
            sid_super_tree,
            settings
            )



        # Create a denoiser for each View Layer
        viewlayer_displace = 0
        view_layer_id = 0
        view_layer: ViewLayer
        for view_layer in scene.view_layers:
            if not view_layer.use:
                continue
            view_layer_id += 1

            # Look for existing Render Layer
            renlayers_node: Node = next(
                (n for n in ntree.nodes
                    if n.bl_idname == 'CompositorNodeRLayers'
                    and n.layer == view_layer.name
                ),
                None
                )
            composite_node: Node = None
            sid_node: Node = None
            output_file_node: Node = None
            temporal_output_file_node: Node = None

            # Sockets to connect to the SID Node
            connect_sockets: List[NodeSocket] = []

            if settings.compositor_reset:
                if renlayers_node:
                    ### Scenarios

                    ## Existing SID setup, we can refresh
                    # Render Layer
                    # +-- SID
                    # | +-- Composite Output (hopefully)
                    # | +-- SID mlEXR File Output (maybe)
                    # | \-- Other existing Node(s)
                    # |   ⁞
                    # |   \-- Composite Output (maybe)
                    # +-- Composite Output (maybe; will be deleted if found)
                    # \-- Other existing Node(s)
                    # We refresh the SID node and ensure there is a Composite Output somewhere.
                    # If there is no Composite Output detected, attach one to SID Node.
                    # If there is a Composite Output attached via the Render Layer,
                    # it will be deleted and recreated, attached to the SID Node.
                    # If there is a SID mlEXR File Output, it will be deleted and recreated.

                    ## Existing custom (or empty) compositor setup (without SID)
                    # Render Layer (hopefully)
                    # +-- Composite Output (hopefully)
                    # \-- Other existing Node(s)
                    #   ⁞
                    #   \-- Composite Output (maybe)
                    # Need to create a SID Node (and mlEXR File Output Node).
                    # Any direct links to other Nodes will be preserved, unless
                    # they come from the Image socket. In that case, they will be
                    # reconnected via the SID Node output.
                    # If there is no Composite Output detected, attach one to SID Node.

                    # Look for any existing SID mlEXR File Output node
                    output_file_node = find_node(renlayers_node, is_sid_mlexr_file_output, True)
                    if output_file_node:
                        # Delete the File Output node; we'll recreate it later with
                        # the correct passes, if needed
                        ntree.nodes.remove(output_file_node)
                        output_file_node = None

                    # Look for any existing SID Temporal mlEXR File Output node
                    temporal_output_file_node = find_node(renlayers_node, is_sid_temporal_output, True)
                    if temporal_output_file_node:
                        # Delete the File Output node; we'll recreate it later with
                        # the correct passes, if needed
                        ntree.nodes.remove(temporal_output_file_node)
                        temporal_output_file_node = None

                    # Look for existing SID Node connected to Render Layer
                    sid_node = find_node(renlayers_node, is_sid_super_group, False)

                    if sid_node:
                        # Existing SID compositor scenario

                        # Look for a Composite Output node somewhere via the SID Node
                        composite_node = find_node(sid_node, is_composite_output, True)

                        # If the Composite Output is already connected via the SID Node,
                        # that's great, we can leave it there.

                        # Reconnect every node connected to the SID Node
                        out_node: NodeSocket
                        for out_node in sid_node.outputs:
                            link: NodeLink
                            for link in out_node.links:
                                if not link.is_valid:
                                    continue
                                connect_sockets.append(link.to_socket)

                        if not composite_node:
                            # Check if there might be a Composite Output node somewhere,
                            # but not connected via the SID Node. If so, delete it.
                            # We'll recreate it afterwards, attached to the SID Node.
                            composite_node = find_node(renlayers_node, is_composite_output, True)
                            if composite_node:
                                # Delete the Composite Output node; we'll recreate it later
                                ntree.nodes.remove(composite_node)
                                composite_node = None

                    else:
                        # No SID Node was found directly connected to the Render Layer.
                        # Look for one attached some other way, and delete it if found,
                        # because this is not considered valid.
                        sid_node = find_node(renlayers_node, is_sid_super_group, True)
                        if sid_node:
                            # Look for an attached Composite Output node, and delete it if found.
                            # We'll recreate it afterwards, attached to the new SID Node.
                            composite_node = find_node(sid_node, is_composite_output, True)
                            if composite_node:
                                # Delete the Composite Output node; we'll recreate it later
                                ntree.nodes.remove(composite_node)
                                composite_node = None

                            # Delete the SID Node; we'll recreate it later
                            print("Warning: deleting a SID node that was INDIRECTLY connected "
                                "to the Render Layer.")
                            ntree.nodes.remove(sid_node)
                            sid_node = None

                    if not sid_node:
                        # Look for an attached Composite Output node. If we find one,
                        # that's great, we can leave it there.
                        composite_node = find_node(renlayers_node, is_composite_output, True)

                    # Output links from "Image" socket should have a SID connected in-between
                    link: NodeLink
                    for link in renlayers_node.outputs['Image'].links:
                        if not link.is_valid:
                            continue

                        # Ignore if for some reason it's linked to the SID node
                        if is_sid_super_group(link.to_node):
                            continue

                        connect_sockets.append(link.to_socket)


            if not renlayers_node:
                #Create Basic Nodes
                renlayers_node = ntree.nodes.new(type='CompositorNodeRLayers')

                renlayers_node.location = (-100, viewlayer_displace)
                renlayers_node.layer = view_layer.name
                renlayers_node.name = "Render Layer"

            if not sid_node:
                sid_node = ntree.nodes.new('CompositorNodeGroup')
                sid_node.location = (200, viewlayer_displace)

            sid_node.node_tree = sid_super_group
            sid_node.name = "sid_node"

            if not composite_node:
                composite_node = ntree.nodes.new(type='CompositorNodeComposite')
                composite_node.location = (400, viewlayer_displace)
                composite_node.name = "Output Node"

                connect_sockets.append(composite_node.inputs['Image'])

            if settings.use_mlEXR:
                # Create the MultiLayer EXR File Output
                output_file_node = ntree.nodes.new(type='CompositorNodeOutputFile')
                output_file_node.name = "mlEXR Node"
                output_file_node.location = (400, viewlayer_displace - 200)
                output_file_node.format.file_format = 'OPEN_EXR_MULTILAYER'

            if settings.denoiser_type == "SID TEMPORAL":
                temporal_output_file_node = ntree.nodes.new(type='CompositorNodeOutputFile')
                temporal_output_file_node.name = "Temporal Output"
                temporal_output_file_node.location = (400, viewlayer_displace - 500)
                temporal_output_file_node.format.file_format = 'OPEN_EXR_MULTILAYER'
                temporal_output_file_node.format.exr_codec = 'ZIP'
                if settings.SIDT_OUT_Compressed:
                    temporal_output_file_node.format.color_depth = '16'
                else:
                    temporal_output_file_node.format.color_depth = '32'


            ##############
            ### CYCLES ###
            ##############

            if RenderEngine == 'CYCLES':
                create_cycles_passes(settings, context, renlayers_node, sid_node, view_layer, output_file_node, connect_sockets, temporal_output_file_node, view_layer_id)

            ###############
            ### LUXCORE ###
            ###############

            if RenderEngine == 'LUXCORE':
                create_luxcore_passes(settings, context, renlayers_node, sid_node, view_layer, output_file_node, connect_sockets)

            ##############
            ### OCTANE ###
            ##############

            if RenderEngine == 'octane':
                create_octane_passes(settings, context, renlayers_node, sid_node, view_layer, output_file_node, connect_sockets)
                
            #################
            ### RENDERMAN ###
            #################

            if RenderEngine == 'PRMAN_RENDER':
                create_renderman_passes(settings, context, renlayers_node, sid_node, view_layer, output_file_node, connect_sockets)

            viewlayer_displace -= 1000

        return {'FINISHED'}
    