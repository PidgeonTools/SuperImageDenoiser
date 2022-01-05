import bpy
from bpy.types import (
    Context,
    Panel,
)
from .SID_Settings import SID_Settings

class SID_PT_Panel:
    bl_label = "Create Super Denoiser"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {"DEFAULT_CLOSED"}

class SID_PT_SID_Panel(SID_PT_Panel, Panel):
    bl_label = "Create Super Denoiser"

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon='SHADERFX')

    def draw(self, context: Context):
        layout = self.layout
        scene = context.scene
        settings: SID_Settings = scene.sid_settings
        RenderEngine = scene.render.engine

        layout.use_property_split = True

        CompatibleWith = [
            'CYCLES',
            'LUXCORE',
            'octane',
            'PRMAN_RENDER'
        ]

        if not RenderEngine in CompatibleWith:
            cycles_warning = layout.column(align=True)
            cycles_warning.label(
                text="SID is not yet compatible with this render engine.", icon='ERROR'
                )
            cycles_warning.label(
                text="       Please change the render engine to a compatible one."
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
            if RenderEngine == 'octane':
                quality.label(
                    text="Renderer does not support super quality.", icon='INFO'
                    )
                quality.label(
                    text="       Will use high quality setting instead"
                )
            else:
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
            
            subpasses = passes.row(align=True)
            subpasses.use_property_split = False

            ##############
            ### CYCLES ###
            ##############
            if RenderEngine == 'CYCLES':
                subpasses.prop(
                    settings,
                    "use_emission",
                    text="Emission",
                    toggle=True
                    )
                subpasses.prop(
                    settings,
                    "use_transmission",
                    text="Transmission",
                    toggle=True
                    )
                subpasses.prop(
                    settings,
                    "use_environment",
                    text="Environment",
                    toggle=True
                    )

                subpasses.prop(
                    settings,
                    "use_volumetric",
                    text="Volumetric",
                    toggle=True
                    )
            ###############
            ### LUXCORE ###
            ###############
            if RenderEngine == 'LUXCORE':   
                subpasses.prop(
                    settings,
                    "use_emission",
                    text="Emission",
                    toggle=True
                    )
                subpasses.prop(
                    settings,
                    "use_transmission",
                    text="Transmission",
                    toggle=True
                    )
                if settings.use_transmission and settings.use_emission:
                    subpasses.prop(
                        settings,
                        "use_caustics",
                        text="Caustics",
                        toggle=True
                        )
            ##############
            ### OCTANE ###
            ##############
            if RenderEngine == 'octane':    
                subpasses.prop(
                    settings,
                    "use_emission",
                    text="Emission",
                    toggle=True
                    )
                subpasses.prop(
                    settings,
                    "use_refraction",
                    text="Refraction",
                    toggle=True
                    )
                subpasses.prop(
                    settings,
                    "use_transmission",
                    text="Transmission",
                    toggle=True
                    )
                subpasses.prop(
                    settings,
                    "use_sss",
                    text="SSS",
                    toggle=True
                    )
                subpasses.prop(
                    settings,
                    "use_volumetric",
                    text="Volumetric",
                    toggle=True
                    )
            #################
            ### RENDERMAN ###
            #################
            if RenderEngine == 'PRMAN_RENDER':
                subpasses.prop(
                    settings,
                    "use_emission",
                    text="Emission",
                    toggle=True
                    )
                subpasses.prop(
                    settings,
                    "use_sss",
                    text="SSS",
                    toggle=True
                    )

            layout.separator()

        advanced = layout.column(align=True)
        advanced.label(
            text="Advanced:"
            )
        #advanced.prop(settings,"compositor_reset",text="refresh SID")
        layout.separator()

        if settings.quality != "STANDARD":
            advanced.prop(settings, "use_mlEXR", text="Use Multi-Layer EXR")
            layout.separator()

        layout.operator("object.superimagedenoise", icon='SHADERFX')
        
        layout.operator("object.superimagedenoise", text="Refresh Super Denoiser", icon='FILE_REFRESH')


class SID_PT_SOCIALS_Panel(SID_PT_Panel, Panel):
    bl_label = "Our Socials"
    bl_parent_id = "SID_PT_SID_Panel"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="FUND")

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        op = col.operator("wm.url_open", text="Join our Discord!", icon="URL")
        op.url = "https://discord.gg/cnFdGQP"
        layout.separator()        
        op = col.operator("wm.url_open", text="Our YouTube Channel!", icon="URL")
        op.url = "https://www.youtube.com/channel/UCgLo3l_ZzNZ2BCQMYXLiIOg"
        op = col.operator("wm.url_open", text="Our BlenderMarket!", icon="URL")
        op.url = "https://blendermarket.com/creators/kevin-lorengel"   
        op = col.operator("wm.url_open", text="Our Instagram Page!", icon="URL")
        op.url = "https://www.instagram.com/pidgeontools/"    
        op = col.operator("wm.url_open", text="Our Twitter Page!", icon="URL")
        op.url = "https://twitter.com/PidgeonTools"
        layout.separator()     
        op = col.operator("wm.url_open", text="Feedback", icon="URL")
        op.url = "https://discord.gg/cnFdGQP"
    