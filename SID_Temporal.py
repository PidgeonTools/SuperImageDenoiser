import bpy
import os
import re
import unicodedata
from bpy.types import Context, Event, Operator, Scene, Timer, ViewLayer
from math import ceil, log10
from .SID_Settings import SID_DenoiseRenderStatus, SID_Settings
from typing import List, NamedTuple

is_save_buffers_supported = bpy.app.version < (3, 0, 0)
is_temporal_nlm_supported = bpy.app.version < (3, 0, 0)
is_temporal_optix_supported = bpy.app.version >= (3, 1, 0)
is_temporal_supported = is_temporal_nlm_supported or is_temporal_optix_supported

# disable uneeded passes for better performance

class SavedRenderSettings(NamedTuple):
    old_view_layer: ViewLayer
    old_pass_im: bool
    old_pass_ze: bool
    old_pass_mt: bool
    old_pass_nr: bool
    old_pass_vc: bool
    old_pass_uv: bool
    old_pass_dn: bool
    old_pass_oi: bool
    old_pass_mi: bool
    old_pass_dd: bool
    old_pass_di: bool
    old_pass_dc: bool
    old_pass_gd: bool
    old_pass_gi: bool
    old_pass_gc: bool
    old_pass_td: bool
    old_pass_ti: bool
    old_pass_tc: bool
    old_pass_vd: bool
    old_pass_vi: bool
    old_pass_em: bool
    old_pass_en: bool
    old_pass_sh: bool
    old_pass_ao: bool
    old_file_format: str
    old_compositor: bool
    old_sequencer: bool
    old_use_single_layer: bool
    old_path: bool
    old_usedenoise: bool
    old_denoiser: str
    old_saveBuffers: bool

class RenderJob(NamedTuple):
    view_layer: ViewLayer


def save_render_settings(context: Context, view_layer: ViewLayer):
    scene = context.scene
    render = scene.render

    old_use_save_buffers = False
    if is_save_buffers_supported:
        old_use_save_buffers = scene.render.use_save_buffers

    return SavedRenderSettings(
        old_view_layer = context.window.view_layer,
        old_pass_im = view_layer.use_pass_combined,
        old_pass_ze = view_layer.use_pass_z,
        old_pass_mt = view_layer.use_pass_mist,
        old_pass_nr = view_layer.use_pass_normal,
        old_pass_vc = view_layer.use_pass_vector,
        old_pass_uv = view_layer.use_pass_uv,
        old_pass_dn = view_layer.cycles.denoising_store_passes,
        old_pass_oi = view_layer.use_pass_object_index,
        old_pass_mi = view_layer.use_pass_material_index,
        old_pass_dd = view_layer.use_pass_diffuse_direct,
        old_pass_di = view_layer.use_pass_diffuse_indirect,
        old_pass_dc = view_layer.use_pass_diffuse_color,
        old_pass_gd = view_layer.use_pass_glossy_direct,
        old_pass_gi = view_layer.use_pass_glossy_indirect,
        old_pass_gc = view_layer.use_pass_glossy_color,
        old_pass_td = view_layer.use_pass_transmission_direct,
        old_pass_ti = view_layer.use_pass_transmission_indirect,
        old_pass_tc = view_layer.use_pass_transmission_color,
        old_pass_vd = view_layer.cycles.use_pass_volume_direct,
        old_pass_vi = view_layer.cycles.use_pass_volume_indirect,
        old_pass_em = view_layer.use_pass_emit,
        old_pass_en = view_layer.use_pass_environment,
        old_pass_sh = view_layer.use_pass_shadow,
        old_pass_ao = view_layer.use_pass_ambient_occlusion,
        old_file_format = render.image_settings.file_format,
        old_compositor = scene.render.use_compositing,
        old_sequencer = scene.render.use_sequencer,
        old_use_single_layer = scene.render.use_single_layer,
        old_path = scene.render.filepath,
        old_usedenoise = scene.cycles.use_denoising,
        old_denoiser = scene.cycles.denoiser,
        old_saveBuffers = old_use_save_buffers
    )

def restore_render_settings(
        context: Context,
        savedsettings: SavedRenderSettings,
        view_layer: ViewLayer
        ):

    scene = context.scene
    render = scene.render

    context.window.view_layer = savedsettings.old_view_layer
    view_layer.use_pass_combined = savedsettings.old_pass_im
    view_layer.use_pass_z = savedsettings.old_pass_ze
    view_layer.use_pass_mist = savedsettings.old_pass_mt
    view_layer.use_pass_normal = savedsettings.old_pass_nr
    view_layer.use_pass_vector = savedsettings.old_pass_vc
    view_layer.use_pass_uv = savedsettings.old_pass_uv
    view_layer.cycles.denoising_store_passes = savedsettings.old_pass_dn
    view_layer.use_pass_object_index = savedsettings.old_pass_oi
    view_layer.use_pass_material_index = savedsettings.old_pass_mi
    view_layer.use_pass_diffuse_direct = savedsettings.old_pass_dd
    view_layer.use_pass_diffuse_indirect = savedsettings.old_pass_di
    view_layer.use_pass_diffuse_color = savedsettings.old_pass_dc
    view_layer.use_pass_glossy_direct = savedsettings.old_pass_gd
    view_layer.use_pass_glossy_indirect = savedsettings.old_pass_gi
    view_layer.use_pass_glossy_color = savedsettings.old_pass_gc
    view_layer.use_pass_transmission_direct = savedsettings.old_pass_td
    view_layer.use_pass_transmission_indirect = savedsettings.old_pass_ti
    view_layer.use_pass_transmission_color = savedsettings.old_pass_tc
    view_layer.cycles.use_pass_volume_direct = savedsettings.old_pass_vd
    view_layer.cycles.use_pass_volume_indirect = savedsettings.old_pass_vi
    view_layer.use_pass_emit = savedsettings.old_pass_em
    view_layer.use_pass_environment = savedsettings.old_pass_en
    view_layer.use_pass_shadow = savedsettings.old_pass_sh
    view_layer.use_pass_ambient_occlusion = savedsettings.old_pass_ao
    render.image_settings.file_format = savedsettings.old_file_format
    scene.render.use_compositing = savedsettings.old_compositor
    scene.render.use_sequencer = savedsettings.old_compositor
    scene.render.use_single_layer = savedsettings.old_use_single_layer
    scene.render.filepath = savedsettings.old_path
    scene.cycles.use_denoising = savedsettings.old_usedenoise
    scene.cycles.denoiser = savedsettings.old_denoiser

    if is_save_buffers_supported:
        scene.render.use_save_buffers = savedsettings.old_saveBuffers


def slugify(value: str) -> str:
    """
    Converts to ASCII. Converts spaces and repeated dashes to single dashes.
    Removes characters that aren't alphanumeric, underscores, or hyphens.
    Converts to lowercase. Also strips leading and trailing whitespace, dashes,
    and underscores.
    Taken from https://stackoverflow.com/a/295466
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def ShowMessageBox(message: str = "", title = "Information", icon = 'INFO'):

    def draw(self, context: Context):
        lines = message.splitlines()
        for line in lines:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


class TD_OT_Render(Operator):
    bl_idname = "object.temporaldenoise_render"
    bl_label = "Render Noisy Frames 1/2"
    bl_description = "Renders the Noisy images with the correct settings, step 1 of 2"

    timer: Timer = None
    stop: bool = False
    rendering: bool = False
    done: bool = False
    jobs: List[RenderJob] = []
    current_job: RenderJob = None
    saved_settings: SavedRenderSettings = None

    # Render callbacks
    def render_pre(self, scene: Scene, dummy):
        self.rendering = True

    def render_post(self, scene: Scene, dummy):
        self.rendering = False

    def render_complete(self, scene: Scene, dummy):
        self.jobs.pop(0)
        self.done = True

    def render_cancel(self, scene: Scene, dummy):
        self.stop = True


    @classmethod
    def poll(cls, context: Context):
        if not is_temporal_supported: return False

        scene = context.scene
        settings: SID_Settings = scene.sid_settings
        denoise_render_status: SID_DenoiseRenderStatus = settings.denoise_render_status

        return not denoise_render_status.is_rendering

    def execute(self, context: Context):
        scene = context.scene

        settings: SID_Settings = scene.sid_settings
        denoise_render_status: SID_DenoiseRenderStatus = settings.denoise_render_status

        # Reset state
        self.stop = False
        self.rendering = False
        self.done = False
        self.jobs = []
        self.current_job = None
        denoise_render_status.is_rendering = True
        denoise_render_status.should_stop = False

        # Prepare render jobs
        job = RenderJob(
            view_layer = context.view_layer
        )
        self.jobs.append(job)

        # Attach render callbacks
        bpy.app.handlers.render_pre.append(self.render_pre)
        bpy.app.handlers.render_post.append(self.render_post)
        bpy.app.handlers.render_cancel.append(self.render_cancel)
        bpy.app.handlers.render_complete.append(self.render_complete)

        # Setup timer and modal
        self.timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context: Context, event: Event):
        scene = context.scene

        settings: SID_Settings = scene.sid_settings
        denoise_render_status: SID_DenoiseRenderStatus = settings.denoise_render_status

        if event.type == 'ESC':
            self.stop = True

        elif event.type == 'TIMER':
            was_cancelled = self.stop or denoise_render_status.should_stop

            if was_cancelled or not self.jobs:
                print("\nStopping.")

                # Remove callbacks
                bpy.app.handlers.render_pre.remove(self.render_pre)
                bpy.app.handlers.render_post.remove(self.render_post)
                bpy.app.handlers.render_cancel.remove(self.render_cancel)
                bpy.app.handlers.render_complete.remove(self.render_complete)
                context.window_manager.event_timer_remove(self.timer)

                denoise_render_status.should_stop = False
                denoise_render_status.is_rendering = False

                if self.current_job:
                    self.cleanup_job(context, self.current_job)

                if was_cancelled:
                    return {'CANCELLED'}
                return {'FINISHED'}

            elif self.done or not self.current_job:
                if self.current_job:
                    self.cleanup_job(context, self.current_job)

                job = self.jobs[0]

                self.start_job(context, job)

        # Allow stop button to cancel rendering rather than this modal
        return {'PASS_THROUGH'}

    def start_job(self, context: Context, job: RenderJob):
        self.current_job = job
        self.done = False

        scene = context.scene
        view_layer = job.view_layer

        self.saved_settings = save_render_settings(context, view_layer)

        ### Setup scene and view layer ###
        # denoiser
        scene.cycles.use_denoising = False
        scene.cycles.denoiser = 'OPTIX' if is_temporal_optix_supported else 'NLM'
        # image output
        scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '32'
        scene.render.image_settings.exr_codec = 'ZIP'
        # passes
        view_layer.use_pass_combined = True
        view_layer.use_pass_z = False
        view_layer.use_pass_mist = False
        view_layer.use_pass_normal = False
        view_layer.use_pass_vector = is_temporal_optix_supported
        view_layer.use_pass_uv = False
        view_layer.cycles.denoising_store_passes = True
        view_layer.use_pass_object_index = False
        view_layer.use_pass_material_index = False
        view_layer.cycles.use_pass_debug_render_time = False
        view_layer.cycles.use_pass_debug_sample_count = False
        view_layer.use_pass_diffuse_direct = False
        view_layer.use_pass_diffuse_indirect = False
        view_layer.use_pass_diffuse_color = False
        view_layer.use_pass_glossy_direct = False
        view_layer.use_pass_glossy_indirect = False
        view_layer.use_pass_glossy_color = False
        view_layer.use_pass_transmission_direct = False
        view_layer.use_pass_transmission_indirect = False
        view_layer.use_pass_transmission_color = False
        view_layer.cycles.use_pass_volume_direct = False
        view_layer.cycles.use_pass_volume_indirect = False
        view_layer.use_pass_emit = False
        view_layer.use_pass_environment = False
        view_layer.use_pass_shadow = False
        view_layer.use_pass_ambient_occlusion = False
        scene.render.use_compositing = False
        scene.render.use_sequencer = False
        if is_save_buffers_supported:
            scene.render.use_save_buffers = False
        # render only this view layer
        scene.render.use_single_layer = True
        context.window.view_layer = view_layer

        ### Render ###
        print(f"Rendering View Layer '{view_layer.name}' animation to: {scene.render.filepath}")

        bpy.ops.render.render("INVOKE_DEFAULT", animation=True)

    def cleanup_job(self, context: Context, job: RenderJob):
        restore_render_settings(context, self.saved_settings, job.view_layer)

class TD_OT_StopRender(Operator):
    bl_idname = "object.temporaldenoise_render_stop"
    bl_label = "Press ESC to Stop Rendering"
    bl_description = "You must press ESC to stop the rendering process."

    def execute(self, context: Context):
        ShowMessageBox(
            "If you want to stop rendering immediately, you must press ESC.",
            "Press ESC to Stop Rendering"
            )

        return {'FINISHED'}


class TD_OT_Denoise(Operator):

    bl_idname = "object.temporaldenoise_denoise"
    bl_label = "Denoise Noisy Frames 2/2"
    bl_description = "Denoises Noisy Frames, step 2 of 2"

    @classmethod
    def poll(cls, context: Context):
        if not is_temporal_supported: return False

        scene = context.scene
        settings: SID_Settings = scene.sid_settings
        denoise_render_status: SID_DenoiseRenderStatus = settings.denoise_render_status

        return not denoise_render_status.is_rendering

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context: Context):
        layout = self.layout
        layout.label(text="Temporal Denoising can take some time.")
        layout.separator()
        layout.label(text="Blender will appear to freeze. This is normal; please be patient.")
        layout.separator()
        layout.label(text="The noisy frames will be updated in-place, and this operation", icon='ERROR')
        layout.label(text="CANNOT BE UNDONE. If you want to create a backup of your rendered")
        layout.label(text="frames first, please do so BEFORE proceeding.")
        layout.separator()
        layout.label(text="To proceed with denoising, press [OK]", icon='DOT')
        layout.label(text="To cancel, click outside this box", icon='DOT')

    def execute(self, context: Context):
        ####denoise###
        try:
            denoiser_name = "OptiX" if is_temporal_optix_supported else "NLM"
            print(f"Running {denoiser_name} Temporal Denoiser, please wait...")

            bpy.ops.cycles.denoise_animation()

            message_text = f"{denoiser_name} Temporal Denoising is finished!"
            self.report({'INFO'}, message_text)
            ShowMessageBox(
                message_text
            )

        except Exception as err:
            err_text = err.__str__()
            self.report({'ERROR'}, err_text.strip())
            ShowMessageBox(
                err_text,
                "An error occurred while Temporal Denoising",
                'ERROR'
            )

        return {'FINISHED'}
