import bpy
import os
from bpy.types import Context, Event, Operator, Scene, Timer, ViewLayer
from math import ceil
from ..SID_Settings import SID_DenoiseRenderStatus, SID_Settings, SID_TemporalDenoiserStatus
from .SID_Create_Temporal_Groups import create_temporal_setup
from ..SuperImageDenoiser import SID_Create
from typing import List, NamedTuple

# disable uneeded passes for better performance
class SavedRenderSettings(NamedTuple):
    old_file_format: str
    old_color_mode: str
    old_color_depth: str
    old_file_path: str
    old_lens: float
    old_res: int

class RenderJob(NamedTuple):
    filepath: str
    view_layer: ViewLayer
    view_layer_id: int

def save_render_settings(context: Context):
    scene = context.scene

    return SavedRenderSettings(
        old_file_format = scene.render.image_settings.file_format,
        old_color_mode = scene.render.image_settings.color_mode,
        old_color_depth = scene.render.image_settings.color_depth,
        old_file_path = scene.render.filepath,
        old_lens = scene.camera.data.lens,
        old_res = scene.render.resolution_percentage
    )

def restore_render_settings(context: Context,savedsettings: SavedRenderSettings):
    scene = context.scene

    scene.render.image_settings.file_format = savedsettings.old_file_format
    scene.render.image_settings.color_mode = savedsettings.old_color_mode
    scene.render.image_settings.color_depth = savedsettings.old_color_depth
    scene.render.filepath = savedsettings.old_file_path
    scene.camera.data.lens = savedsettings.old_lens
    scene.render.resolution_percentage = savedsettings.old_res

def setup_render_settings(context: Context):
    scene = context.scene
    settings: SID_Settings = scene.sid_settings
    

    ### Setup scene and view layer ###
    # image output
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.render.filepath = os.path.join(settings.inputdir,"preview")
    scene.camera.data.lens = scene.camera.data.lens * (1-(((100 + settings.SIDT_Overscan_Amount) / 100)-1))
    scene.render.resolution_percentage = ceil(scene.render.resolution_percentage * ((100 + settings.SIDT_Overscan_Amount) / 100))
        
def create_jobs(scene: Scene) -> List[RenderJob]:
    settings: SID_Settings = scene.sid_settings

    jobs: List[RenderJob] = []

    # number of digits required to represent a decimal number (e.g. 42 -> 2)
    layer_counter = 0
    for view_layer in scene.view_layers:
        layer_counter += 1

        if not view_layer.use:
            continue

        # e.g. "1/000001.exr" or "01/000001.exr", etc.
        view_layer_directory = f"{layer_counter}"
        settings.filename = view_layer_directory
        filepath = os.path.join(settings.inputdir, "preview", view_layer_directory, "######")
        job = RenderJob(
            filepath = filepath,
            view_layer = view_layer,
            view_layer_id = layer_counter
        )
        jobs.append(job)

    return jobs

def create_render_job(scene: Scene) -> List[RenderJob]:
    settings: SID_Settings = scene.sid_settings

    jobs: List[RenderJob] = []

    # number of digits required to represent a decimal number (e.g. 42 -> 2)
    layer_counter = 0
    for view_layer in scene.view_layers:

        filepath = os.path.join(settings.inputdir, "preview", "######")
        job = RenderJob(
            filepath = filepath,
            view_layer = view_layer,
            view_layer_id = layer_counter
        )
        if layer_counter == 0: jobs.append(job)

        layer_counter += 1

    return jobs


def ShowMessageBox(message: str = "", title = "Information", icon = 'INFO'):

    def draw(self, context: Context):
        lines = message.splitlines()
        for line in lines:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

class SIDT_OT_RenderFG(Operator):
    bl_idname = "object.superimagedenoisetemporal"
    bl_label = "1/2 - Render with SID Temporal"
    bl_description = "Enables all the necessary passes, Creates all the nodes you need, connects them all for you, renders and denoises the frames"

    timer: Timer = None
    stop: bool = False
    rendering: bool = False
    done: bool = False
    jobs: List[RenderJob] = []
    current_job: RenderJob = None

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

        # Prepare render jobs
        self.jobs = create_render_job(scene)
        self.current_job = None

        denoise_render_status.is_rendering = True
        denoise_render_status.should_stop = False
        denoise_render_status.jobs_done = 0
        denoise_render_status.jobs_remaining = denoise_render_status.jobs_total = len(self.jobs)

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
                    self.cleanup_job(context)
                    
                if was_cancelled:
                    return {'CANCELLED'}
                return {'FINISHED'}

            elif self.done or not self.current_job:
                if self.current_job:
                    self.cleanup_job(context)

                self.start_job(context)

                denoise_render_status.jobs_done += 1
                denoise_render_status.jobs_remaining -= 1

        # Allow stop button to cancel rendering rather than this modal
        return {'PASS_THROUGH'}

    def start_job(self, context: Context):
        self.done = False

        scene = context.scene
        settings: SID_Settings = scene.sid_settings

        self.saved_settings = save_render_settings(context)

        ### Setup scene and view layer ###
        setup_render_settings(context)

        SID_Create.execute(self, context)
        scene.render.filepath = os.path.join(settings.inputdir,"preview","######")

        print(f"Rendering animation to: {scene.render.filepath}")
        bpy.ops.render.render("INVOKE_DEFAULT", animation=True)
        
    def cleanup_job(self, context: Context):
        restore_render_settings(context, self.saved_settings)

class SIDT_OT_StopRender(Operator):
    bl_idname = "object.superimagedenoisetemporal_stop"
    bl_label = "Press ESC to Stop Rendering"
    bl_description = "You must press ESC to stop the rendering process."

    def execute(self, context: Context):
        ShowMessageBox(
            "If you want to stop rendering immediately, you must press ESC.",
            "Press ESC to Stop Rendering"
            )

        return {'FINISHED'}

class SIDT_OT_DenoiseFG(Operator):
    bl_idname = "object.superimagedenoisealign"
    bl_label = "2/2 - Denoise with SID Temporal"
    bl_description = "Step two of the Temporal Denoising process. This will align the frames and denoise them."

    timer: Timer = None
    stop: bool = False
    running: bool = False
    done: bool = False
    jobs: List[RenderJob] = []
    current_job: RenderJob = None

    @classmethod
    def poll(cls, context: Context):

        scene = context.scene
        settings: SID_Settings = scene.sid_settings
        temporal_denoiser_status: SID_TemporalDenoiserStatus = settings.temporal_denoiser_status

        return not temporal_denoiser_status.is_running

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context: Context):
        layout = self.layout
        layout.label(text="Temporal Denoising can take some time.")
        layout.separator()
        layout.label(text="Blender will appear to freeze. This is normal; please be patient.")
        layout.separator()
        layout.label(text="The denoised frames will be added in the directory")
        layout.separator()
        layout.label(text="To proceed with denoising, press [OK]", icon='DOT')
        layout.label(text="To cancel, click outside this box", icon='DOT')

    def execute(self, context: Context):
        scene = context.scene

        settings: SID_Settings = scene.sid_settings
        temporal_denoiser_status: SID_TemporalDenoiserStatus = settings.temporal_denoiser_status

        # Reset state
        self.stop = False
        self.running = True
        self.done = False

        # Prepare denoising jobs
        self.jobs = create_jobs(scene)
        self.current_job = None

        temporal_denoiser_status.is_running = True
        temporal_denoiser_status.should_stop = False
        temporal_denoiser_status.jobs_done = 0
        temporal_denoiser_status.jobs_remaining = temporal_denoiser_status.jobs_total = len(self.jobs)

        # Setup timer and modal
        self.timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context: Context, event: Event):
        scene = context.scene
        settings: SID_Settings = scene.sid_settings
        temporal_denoiser_status: SID_TemporalDenoiserStatus = settings.temporal_denoiser_status

        if event.type == 'ESC':
            self.stop = True

        elif event.type == 'TIMER':
            was_cancelled = self.stop or temporal_denoiser_status.should_stop

            if was_cancelled or not self.jobs:
                print("\nStopping.")
                self.running = False

                # Remove callbacks
                context.window_manager.event_timer_remove(self.timer)

                temporal_denoiser_status.should_stop = False
                temporal_denoiser_status.is_running = False

                if was_cancelled:
                    return {'CANCELLED'}

                message_text = "Temporal Denoising is finished!"
                self.report({'INFO'}, message_text)
                ShowMessageBox(message_text)
                return {'FINISHED'}

            elif self.done or not self.current_job:

                job = self.jobs[0]

                self.start_job(context, job)

                temporal_denoiser_status.jobs_done += 1
                temporal_denoiser_status.jobs_remaining -= 1

        return {'PASS_THROUGH'}

    def start_job(self, context: Context, job: RenderJob):
        self.current_job = job
        self.done = False
        self.running = True

        scene = context.scene

        ### Denoise ###
        try:
            scene = context.scene
            settings: SID_Settings = scene.sid_settings
            TDScene = bpy.data.scenes[scene.name].copy()

            for view_layers in TDScene.view_layers:
                view_layers.use = False
            
            view_layers.use = True

            create_temporal_setup(TDScene,settings,job.view_layer_id)

            bpy.data.scenes.remove(TDScene)

            self.done = True
            self.jobs.pop(0)

        except Exception as err:
            # Don't continue
            self.stop = True

            err_text = err.__str__()
            self.report({'ERROR'}, err_text.strip())
            ShowMessageBox(
                err_text,
                "An error occurred while Temporal Denoising",
                'ERROR'
            )

class SIDT_OT_StopDenoise(Operator):
    bl_idname = "object.superimagedenoisealign_stop"
    bl_label = "Stop Temporal Denoising"
    bl_description = "Stop denoising all View Layers"

    def execute(self, context: Context):
        scene = context.scene
        settings: SID_Settings = scene.sid_settings
        temporal_denoiser_status: SID_TemporalDenoiserStatus = settings.temporal_denoiser_status

        temporal_denoiser_status.should_stop = True

        return {'FINISHED'}
