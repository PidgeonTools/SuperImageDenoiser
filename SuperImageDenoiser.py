import bpy
from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty,
)

from SID_Create_DenoiserGroup import create_sid_super_denoiser_group
from SID_Create_Group import create_sid_super_group
from SID_QualityStandart import create_sid_denoiser_standard
from SID_QualityHigh import create_sid_denoiser_high
from SID_QualitySuper import create_sid_denoiser_super
from SID_Settings import SID_Settings



class SID_Create(Operator):

    bl_idname = "object.superimagedenoise"
    bl_label = "Add Super Denoiser"
    bl_description = "Enables all the necessary passes, Creates all the nodes you need, connects them all for you, to save the time you don't need to waste"

    def execute(self, context):

        scene = context.scene
        settings: SID_Settings = scene.sid_settings

        # Initialise important settings
        scene.render.engine = 'CYCLES'
        scene.use_nodes = True
        RenderLayer = 0


        #Clear Compositor
        ntree = scene.node_tree

        if settings.compositor_reset:
            for node in ntree.nodes:
                ntree.nodes.remove(node)



        #SID

        # Create dual denoiser node group
        SID_standard_tree = create_sid_denoiser_standard()
        SID_high_tree = create_sid_super_denoiser_group(create_sid_denoiser_high(), settings)
        SID_super_tree = create_sid_super_denoiser_group(create_sid_denoiser_super(), settings)

        SID_super_group = create_sid_super_group(SID_standard_tree, SID_high_tree, SID_super_tree, settings)



        # Create a denoiser for each View Layer
        ViewLayerDisplace = 0
        for view_layer in scene.view_layers:

            if not view_layer.use:
                continue

            #Create Basic Nodes
            RenLayers_node = ntree.nodes.new(type='CompositorNodeRLayers')
            RenLayers_node.location = (-100, ViewLayerDisplace)
            RenLayers_node.layer = view_layer.name
            Composite_node = ntree.nodes.new(type='CompositorNodeComposite')
            Composite_node.location = (400, ViewLayerDisplace)

            SID_node = scene.node_tree.nodes.new("CompositorNodeGroup")
            SID_node.node_tree = SID_super_group
            SID_node.location = (200, ViewLayerDisplace)
            SID_node.name = "sid_node"


            # Prepare View Layer

            ###Enable Passes###
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


            ViewLayerDisplace -= 1000

            ntree.links.new(RenLayers_node.outputs["DiffDir"],SID_node.inputs["DiffDir"])
            ntree.links.new(RenLayers_node.outputs["DiffInd"],SID_node.inputs["DiffInd"])
            ntree.links.new(RenLayers_node.outputs["DiffCol"],SID_node.inputs["DiffCol"])
            ntree.links.new(RenLayers_node.outputs["GlossDir"],SID_node.inputs["GlossDir"])
            ntree.links.new(RenLayers_node.outputs["GlossInd"],SID_node.inputs["GlossInd"])
            ntree.links.new(RenLayers_node.outputs["GlossCol"],SID_node.inputs["GlossCol"])

            if settings.use_transmission:
                ntree.links.new(RenLayers_node.outputs["TransDir"],SID_node.inputs["TransDir"])
                ntree.links.new(RenLayers_node.outputs["TransInd"],SID_node.inputs["TransInd"])
                ntree.links.new(RenLayers_node.outputs["TransCol"],SID_node.inputs["TransCol"])

            if settings.use_volumetric:
                ntree.links.new(RenLayers_node.outputs["VolumeDir"],SID_node.inputs["VolumeDir"])
                ntree.links.new(RenLayers_node.outputs["VolumeInd"],SID_node.inputs["VolumeInd"])

            if settings.use_emission:
                ntree.links.new(RenLayers_node.outputs["Emit"],SID_node.inputs["Emit"])

            if settings.use_environment:
                ntree.links.new(RenLayers_node.outputs["Env"],SID_node.inputs["Env"])

            ntree.links.new(RenLayers_node.outputs["Alpha"],SID_node.inputs["Alpha"])
            ntree.links.new(RenLayers_node.outputs["Noisy Image"],SID_node.inputs["Noisy Image"])
            ntree.links.new(RenLayers_node.outputs["Denoising Albedo"],SID_node.inputs["Denoising Albedo"])
            ntree.links.new(RenLayers_node.outputs["Denoising Normal"],SID_node.inputs["Denoising Normal"])

            if settings.quality == 'SUPER':
                ntree.links.new(SID_node.outputs["SUPER Quality"],Composite_node.inputs["Image"])
            elif settings.quality == 'HIGH':
                ntree.links.new(SID_node.outputs["High Quality"],Composite_node.inputs["Image"])
            else:
                ntree.links.new(SID_node.outputs["Standard Quality"],Composite_node.inputs["Image"])

        return {'FINISHED'}

class SID_PT_Panel(Panel):

    bl_label = "Create Super Denoiser"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_category = 'Pidgeon-Tools'

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='SHADERFX')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.sid_settings

        if bpy.context.scene.render.engine != 'CYCLES':
            cycles_warning = layout.column(align=True)
            cycles_warning.label(text="Intel Denoiser (OIDN) render passes require Cycles.", icon='ERROR')
            cycles_warning.label(text="       The Render Engine will be switched to Cycles.")
            layout.separator()

        quality = layout.column(align=True)
        quality.prop(settings, "quality", text="Quality")
        if settings.quality == 'STANDARD':
            quality.label(text="Denoise the whole image in a single pass.", icon='INFO')
            quality.label(text="       Maximum compositing speed and least memory consumption.")
        elif settings.quality == 'HIGH':
            quality.label(text="Denoise related render passes in groups.", icon='INFO')
            quality.label(text="       Moderate compositing speed and increased memory consumption.")
        elif settings.quality == 'SUPER':
            quality.label(text="Denoise each render pass separately.", icon='INFO')
            quality.label(text="       Slowest compositing speed and greatly increased memory consumption.")
        layout.separator()
        


        passes = layout.column(align=True)
        passes.label(text="Render passes:")
        passes.prop(settings, "use_emission", text="Use Emission Pass")
        passes.prop(settings, "use_environment", text="Use Environment Pass")
        passes.prop(settings, "use_transmission", text="Use Transmission Pass")
        passes.prop(settings, "use_volumetric", text="Use Volumetric Pass")
        layout.separator()
        
        advanced = layout.column(align=True)
        advanced.label(text="Advanced:")
        advanced.prop(settings, "compositor_reset", text="reset compositor before adding SID?")
            
        if settings.compositor_reset:
            if bpy.context.scene.use_nodes == True:
                compositor_warn = layout.column(align=True)
                compositor_warn.label(text="Compositor nodes detected!", icon='ERROR')
                compositor_warn.label(text="       Using Super Image Denoiser will delete all compositor nodes!")
                compositor_warn.label(text="       Ignore if you just added Super Image Denoiser.")
                layout.separator()
        
        layout.operator("object.superimagedenoise", icon='SHADERFX')





# Register classes
classes = (
    SID_Settings,
    SID_PT_Panel,
    SID_Create,
)

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.sid_settings = PointerProperty(type=SID_Settings)

def unregister():
    from bpy.utils import unregister_class

    del bpy.types.Scene.sid_settings

    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
