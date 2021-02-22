import bpy
from bpy.types import Operator

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

from . import SID_Settings

class SID_Create(Operator):

    bl_idname = "object.superimagedenoise"
    bl_label = "Add Super Denoiser"
    bl_description = "Enables all the necessary passes, Creates all the nodes you need, connects them all for you, to save the time you don't need to waste"

    def execute(self, context):

        scene = context.scene
        RenderEngine = scene.render.engine
        settings: SID_Settings = scene.sid_settings

        # Initialise important settings
        #if scene.render.engine is not 'CYCLES' or not 'LUXCORE':
        #    scene.render.engine = 'CYCLES'
        scene.use_nodes = True


        #Clear Compositor
        ntree = scene.node_tree

        
        node_exists = ntree.nodes.get("Composite", None)
        if node_exists is not None:
            ntree.nodes.remove(node_exists)



        #SID

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
#        elif RenderEngine == 'octane':
#            sid_super_tree = create_sid_super_denoiser_group(
#                create_sid_denoiser_super_oc(),
#                settings
#                )
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
        for view_layer in scene.view_layers:

            if not view_layer.use:
                continue

            # Prepare View Layer

            #check for missing node
            node_exists = ntree.nodes.get("sid_node", None)

            output_file_node = None
            if settings.compositor_reset and node_exists is not None:
                
                #repair
                sid_node = ntree.nodes["sid_node"]
                renlayers_node = ntree.nodes["Render Layer"]
                composite_node = ntree.nodes["Output Node"]

                node_exists = ntree.nodes.get("mlEXR Node", None)
                if node_exists is not None:
                    if settings.use_mlEXR:
                        ntree.nodes.remove(node_exists)
                        output_file_node = ntree.nodes.new(type="CompositorNodeOutputFile")
                        output_file_node.name = "mlEXR Node"
                        output_file_node.location = (400, viewlayer_displace - 200)
                    else:
                        ntree.nodes.remove(node_exists)
                else:
                    if settings.use_mlEXR:
                        output_file_node = ntree.nodes.new(type="CompositorNodeOutputFile")
                        output_file_node.name = "mlEXR Node"
                        output_file_node.location = (400, viewlayer_displace - 200)
                

            else:
                #Create Basic Nodes
                renlayers_node = ntree.nodes.new(type='CompositorNodeRLayers')

                renlayers_node.location = (-100, viewlayer_displace)
                renlayers_node.layer = view_layer.name
                renlayers_node.name = "Render Layer"

                sid_node = ntree.nodes.new("CompositorNodeGroup")
                sid_node.node_tree = sid_super_group
                
                composite_node = ntree.nodes.new(type='CompositorNodeComposite')
                composite_node.location = (400, viewlayer_displace)
                composite_node.name = "Output Node"

                if settings.use_mlEXR:
                    output_file_node = ntree.nodes.new(type="CompositorNodeOutputFile")
                    output_file_node.name = "mlEXR Node"
                    output_file_node.location = (400, viewlayer_displace - 200)

            sid_node.node_tree = sid_super_group
            sid_node.location = (200, viewlayer_displace)
            sid_node.name = "sid_node"

            ##############
            ### CYCLES ###
            ##############

            if RenderEngine == 'CYCLES':
                sid_node = create_cycles_passes(settings, context, renlayers_node, sid_node, view_layer, output_file_node, composite_node)



            ###############
            ### LUXCORE ###
            ###############

            if RenderEngine == 'LUXCORE':
                sid_node = create_luxcore_passes(settings, context, renlayers_node, sid_node, view_layer, output_file_node, composite_node)
                
            ##############
            ### OCTANE ###
            ##############

            if RenderEngine == 'octane':
                sid_node = create_octane_passes(settings, context, renlayers_node, sid_node, view_layer, output_file_node, composite_node)


            composite_node.location = (400, viewlayer_displace)
            viewlayer_displace -= 1000
            return {'FINISHED'}
