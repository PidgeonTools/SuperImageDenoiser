import bpy

from bpy.types import (
    Panel,
)
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
            cycles_warning.label(
                text="Intel Denoiser (OIDN) render passes require Cycles.", icon='ERROR'
                )
            cycles_warning.label(
                text="       The Render Engine will be switched to Cycles."
                )
            layout.separator()

        quality = layout.column(align=True)
        quality.prop(
            settings,
            "quality",
            text="Quality"
            )
        if settings.quality == 'STANDARD':
            quality.label(
                text="Denoise the whole image in a single pass.",
                icon='INFO'
                )
            quality.label(
                text="       Maximum compositing speed and least memory consumption."
                )
        elif settings.quality == 'HIGH':
            quality.label(
                text="Denoise related render passes in groups.", icon='INFO'
                )
            quality.label(
                text="       Moderate compositing speed and increased memory consumption."
                )
        elif settings.quality == 'SUPER':
            quality.label(
                text="Denoise each render pass separately.", icon='INFO'
                )
            quality.label(
                text="       Slowest compositing speed and greatly increased memory consumption."
                )
        layout.separator()

        if settings.quality != "STANDARD":
            passes = layout.column(align=True)
            passes.label(
                text="Render passes:"
                )
            passes.prop(
                settings,
                "use_emission",
                text="Use Emission Pass"
                )
            passes.prop(
                settings,
                "use_environment",
                text="Use Environment Pass"
                )
            passes.prop(
                settings,
                "use_transmission",
                text="Use Transmission Pass"
                )
            passes.prop(
                settings,
                "use_volumetric",
                text="Use Volumetric Pass"
                )
            layout.separator()

        advanced = layout.column(align=True)
        advanced.label(
            text="Advanced:"
            )
        advanced.prop(
            settings,
            "compositor_reset",
            text="reset compositor before adding SID?"
            )

        if settings.compositor_reset:
            if bpy.context.scene.use_nodes == True:
                compositor_warn = layout.column(align=True)
                compositor_warn.label(
                    text="Compositor nodes detected!", icon='ERROR'
                    )
                compositor_warn.label(
                    text="       Using Super Image Denoiser will delete all compositor nodes!"
                    )
                compositor_warn.label(
                    text="       Ignore if you just added Super Image Denoiser."
                    )
                layout.separator()



        if settings.quality != "STANDARD":
            advanced.prop(settings, "use_mlEXR", text="Use Multi-Layer EXR")
            layout.separator()

        layout.operator("object.superimagedenoise", icon='SHADERFX')
