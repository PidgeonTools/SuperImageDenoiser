import typing
import os
import bpy
from bpy.types import (
    Context,
    Panel,
)
from .SID_Settings import SID_DenoiseRenderStatus, SID_Settings, SID_TemporalDenoiserStatus
from .SID_Temporal import is_temporal_supported, is_temporal_optix_supported, is_temporal_nlm_supported

ICON_DIR_NAME = "Icons"

class IconManager:
    def __init__(self, additional_paths: typing.Optional[typing.List[str]] = None):
        import bpy.utils.previews
        self.icon_previews = bpy.utils.previews.new()
        self.additional_paths = additional_paths if additional_paths is not None else []
        self.load_all()

    def load_all(self) -> None:
        icons_dir = os.path.join(os.path.dirname(__file__), ICON_DIR_NAME)
        self.load_icons_from_directory(icons_dir)

        for path in self.additional_paths:
            self.load_icons_from_directory(os.path.join(path, ICON_DIR_NAME))

    def load_icons_from_directory(self, path: str) -> None:
        if not os.path.isdir(path):
            raise RuntimeError(f"Cannot load icons from {path}, it is not valid dir")

        for icon_filename in os.listdir(path):
            self.load_icon(icon_filename, path)

    def load_icon(self, filename: str, path: str) -> None:
        if not filename.endswith((".png")):
            return

        icon_basename, _ = os.path.splitext(filename)
        if icon_basename in self.icon_previews:
            return

        self.icon_previews.load(icon_basename, os.path.join(
            path, filename), "IMAGE")

    def get_icon(self, icon_name: str) -> bpy.types.ImagePreview:
        return self.icon_previews[icon_name]

    def get_icon_id(self, icon_name: str) -> int:
        return self.icon_previews[icon_name].icon_id


icon_manager = IconManager()


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
        denoise_render_status: SID_DenoiseRenderStatus = settings.denoise_render_status
        temporal_denoiser_status: SID_TemporalDenoiserStatus = settings.temporal_denoiser_status
        RenderEngine = scene.render.engine
        view_layer = context.view_layer
        cycles_view_layer = view_layer.cycles

        # do we have to use the old layout engine?
        legacy_layout = bpy.app.version < (2, 90)

        # currently rendering noisy frames?
        is_rendering = denoise_render_status.is_rendering
        is_denoising = temporal_denoiser_status.is_running

        panel_active = not is_rendering and not is_denoising

        layout.use_property_split = True

        #######################
        ### DECIDE DENOISER ###
        #######################
        denoiser_type = settings.denoiser_type if is_temporal_supported else "SID"

        if RenderEngine == "CYCLES" and is_temporal_supported:
            denoiser_type_col = layout.column(align=True)
            denoiser_type_col.active = panel_active

            denoiser_type_col.prop(
                settings,
                "denoiser_type",
                expand=True,
                text="Denoiser Type"
                )

        else:
            # Temporal is not supported
            # - maybe because the Render Engine is not compatible (only Cycles)
            # - maybe because the Blender version is not compatible (removed from 3.0+)
            # so don't show the option to use it
            denoiser_type = "SID"

        if denoiser_type == "SID":
            layout.separator()

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

                # don't draw any more panel settings
                return

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
            layout.separator()

            if settings.quality != "STANDARD":
                advanced.prop(settings, "use_mlEXR", text="Use Multi-Layer EXR")
                layout.separator()

            layout.operator("object.superimagedenoise", icon='SHADERFX')
            
            layout.operator("object.superimagedenoise", text="Refresh Super Denoiser", icon='FILE_REFRESH')

        elif denoiser_type == "SID TEMPORAL":
            layout.separator()

            CompatibleWith = [
                'CYCLES'
            ]

            if not RenderEngine in CompatibleWith:
                cycles_warning = layout.column(align=True)
                cycles_warning.label(
                    text="SID Temporal is not yet compatible with this render engine.", icon='ERROR'
                    )
                cycles_warning.label(
                    text="       Please change the render engine to a compatible one."
                    )
                layout.separator()

                # don't draw any more panel settings
                return

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

                layout.separator()

            fileio = layout.column(align=True)
            fileio.active = panel_active
            fileio.label(text="do not use relative path")
            fileio.prop(settings, "inputdir", text="Image directory")
            fileio.separator()

            fileio.label(text="It's recommended to enable Overwrite existing files")
            fileio.label(text="unless you know what you are doing")
            fileio.prop(scene.render, "use_overwrite", text="Overwrite existing files")

            layout.operator("object.superimagedenoisetemporal", icon='SHADERFX')
            layout.operator("object.superimagedenoisealign", icon='SHADERFX')


        elif denoiser_type == "TEMPORAL" and is_temporal_supported:
            ##### TEMPORAL #####

            denoiser_col = layout.column(align=True)
            denoiser_col.active = panel_active
            denoiser_col.label(text="Temporal usually has inferior denoising quality to SID!", icon='INFO')
            denoiser_col.separator()

            if is_temporal_optix_supported:
                denoiser_col.label(text="Will use OptiX Temporal Denoiser")
            else:
                denoiser_col.label(text="Will use NLM Temporal Denoiser")
            denoiser_col.separator()

            fileio = layout.column(align=True)
            fileio.active = panel_active
            fileio.prop(settings, "inputdir", text="Image directory")
            fileio.separator()

            fileio.label(text="It's recommended to enable Overwrite existing files")
            fileio.label(text="unless you know what you are doing")
            fileio.prop(scene.render, "use_overwrite", text="Overwrite existing files")

            if is_temporal_nlm_supported:
                layout.separator()

                tdsettings = layout.row()
                tdsettings.active = panel_active
                tdsettings.prop(cycles_view_layer, "denoising_radius", text="Radius")
                tdsettings.prop(cycles_view_layer, "denoising_neighbor_frames", text="Range")

                tdsettings = layout.column()
                tdsettings.active = panel_active
                tdsettings.prop(cycles_view_layer, "denoising_strength", slider=True, text="Strength")
                tdsettings.prop(cycles_view_layer, "denoising_feature_strength", slider=True, text="Feature Strength")
                tdsettings.prop(cycles_view_layer, "denoising_relative_pca")

                tdsettings = layout.column()
                tdsettings.active = panel_active and (cycles_view_layer.use_denoising or cycles_view_layer.denoising_store_passes)

                if legacy_layout:
                    split = tdsettings.split(factor=0.5)
                    col = split.column()
                    col.alignment = 'RIGHT'
                    col.label(text="Diffuse")
                    row = split.row(align=True)
                    row.use_property_split = False
                else:
                    row = tdsettings.row(heading="Diffuse", align=True)
                row.prop(cycles_view_layer, "denoising_diffuse_direct", text="Direct", toggle=True)
                row.prop(cycles_view_layer, "denoising_diffuse_indirect", text="Indirect", toggle=True)

                if legacy_layout:
                    split = tdsettings.split(factor=0.5)
                    col = split.column()
                    col.alignment = 'RIGHT'
                    col.label(text="Glossy")
                    row = split.row(align=True)
                    row.use_property_split = False
                else:
                    row = tdsettings.row(heading="Glossy", align=True)
                row.prop(cycles_view_layer, "denoising_glossy_direct", text="Direct", toggle=True)
                row.prop(cycles_view_layer, "denoising_glossy_indirect", text="Indirect", toggle=True)


                if legacy_layout:
                    split = tdsettings.split(factor=0.5)
                    col = split.column()
                    col.alignment = 'RIGHT'
                    col.label(text="Transmission")
                    row = split.row(align=True)
                    row.use_property_split = False
                else:
                    row = tdsettings.row(heading="Transmission", align=True)
                row.prop(cycles_view_layer, "denoising_transmission_direct", text="Direct", toggle=True)
                row.prop(cycles_view_layer, "denoising_transmission_indirect", text="Indirect", toggle=True)

            layout.separator()

            tdrender = layout.column(align=True)
            tdrender.active = panel_active
            if is_rendering:
                tdrender.label(text=f"{denoise_render_status.jobs_done} / {denoise_render_status.jobs_total} View Layers completed", icon='INFO')
                tdrender.prop(denoise_render_status, "percent_complete")
                tdrender.operator("object.temporaldenoise_render_stop", icon='CANCEL')
            else:
                tdrender.operator("object.temporaldenoise_render", icon='RENDER_ANIMATION')
            tdrender.separator()

            tddenoise = layout.column(align=True)
            tddenoise.active = panel_active
            if is_denoising:
                tddenoise.active = True
                tddenoise.label(text=f"{temporal_denoiser_status.jobs_done} / {temporal_denoiser_status.jobs_total} View Layers completed", icon='INFO')
                tddenoise.prop(temporal_denoiser_status, "percent_complete")
                tddenoise.operator("object.temporaldenoise_denoise_stop", icon='CANCEL')
            else:
                tddenoise.operator("object.temporaldenoise_denoise", icon='SHADERFX')


class SID_PT_SOCIALS_Panel(SID_PT_Panel, Panel):
    bl_label = "Our Socials"
    bl_parent_id = "SID_PT_SID_Panel"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="FUND")

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator(
            "wm.url_open",
            text="Join our Discord!",
            icon_value = icon_manager.get_icon_id("Discord")
            ).url = "https://discord.gg/cnFdGQP"
        layout.separator()

        col.operator(
            "wm.url_open",
            text="Our YouTube Channel!",
            icon_value = icon_manager.get_icon_id("Youtube")
            ).url = "https://www.youtube.com/channel/UCgLo3l_ZzNZ2BCQMYXLiIOg"
        col.operator(
            "wm.url_open",
            text="Our BlenderMarket!",
            icon_value = icon_manager.get_icon_id("BlenderMarket")
            ).url = "https://blendermarket.com/creators/kevin-lorengel"   
        col.operator(
            "wm.url_open",
            text="Our Instagram Page!",
            icon_value = icon_manager.get_icon_id("Instagram")
            ).url = "https://www.instagram.com/pidgeontools/"    
        col.operator(
            "wm.url_open",
            text="Our Twitter Page!",
            icon_value = icon_manager.get_icon_id("Twitter")
            ).url = "https://twitter.com/PidgeonTools"
        layout.separator()

        col.operator(
            "wm.url_open",
            text="Support and Feedback!",
            icon="HELP"
            ).url = "https://discord.gg/cnFdGQP"
    
preview_collections = {}