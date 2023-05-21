import bpy
import os
from bpy.types import Context, Operator
from math import ceil
from ..SID_Settings import SID_Settings
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
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.render.filepath = os.path.join(settings.inputdir,"preview")
    scene.camera.data.lens = scene.camera.data.lens * (1-(((100 + settings.SIDT_Overscan_Amount) / 100)-1))
    scene.render.resolution_percentage = ceil(scene.render.resolution_percentage * ((100 + settings.SIDT_Overscan_Amount) / 100))

def ShowMessageBox(message: str = "", title = "Information", icon = 'INFO'):

    bpy.context.window_manager.popup_menu(message, title = title, icon = icon)

class SIDT_OT_RenderBG(Operator):
    bl_idname = "object.superimagedenoisetemporal_bg"
    bl_label = "1/2 - Render with SID Temporal"
    bl_description = "Enables all the necessary passes, Creates all the nodes you need, connects them all for you, renders and denoises the frames"

    def execute(self, context: Context):
        
        #ShowMessageBox(
        #   "During the rendering process there will be no rendering preview. This is normal. Please be patient.\nBlender will freeze and not react to any input.\n\nIf you want to make sure that your render is still running, you can check the console for the current frame.\nTo open the console, go to Window > Toggle System Console.\n\nThis has to be done before you start rendering.\nAdditionally, you will see your rendered images appear in the folder you specified.\n\nIf you want to stop rendering immediately, you must close blender.\n\nTo ensure that your render comes out correctly, please make a test render first.\nWe recommend rendering a few frames with the same settings you want to use for your final render",
        #   "Attention!",
        #   "INFO"
        #)

        scene = context.scene
        settings: SID_Settings = scene.sid_settings

        savedRenderSettings = save_render_settings(context)

        setup_render_settings(context)

        SID_Create.execute(self, context)
        scene.render.filepath = os.path.join(settings.inputdir,"preview","######")

        print(f"Rendering animation to: {scene.render.filepath}")
        bpy.ops.render.render(animation=True)

        restore_render_settings(context, savedRenderSettings)
        
        return {'FINISHED'}

class SIDT_OT_DenoiseBG(Operator):
    bl_idname = "object.superimagedenoisealign_bg"
    bl_label = "2/2 - Denoise with SID Temporal"
    bl_description = "Step two of the Temporal Denoising process. This will align the frames and denoise them."

    def execute(self, context: Context):
        scene = context.scene
        settings: SID_Settings = scene.sid_settings

        # ShowMessageBox(
        #     "During the denoising process there will be no rendering preview. This is normal. Please be patient.",
        #     "Blender will freeze and not react to any input.",
        #     " ",
        #     "If you want to make sure that your render is still running, you can check the console for the current frame.",
        #     "To open the console, go to Window > Toggle System Console.",
        #     "This has to be done before you start denoised.",
        #     "Additionally, you will see your denoised images appear in the folder you specified.",
        #     " ",
        #     "If you want to stop denoised immediately, you must close blender."
        # )

        scene = context.scene
        TDScene = bpy.data.scenes[scene.name].copy()

        for view_layers in TDScene.view_layers:
            view_layers.use = False
        
        view_layers.use = True

        #for each folder in the input directory get the name
        noisyPath = os.path.join(settings.inputdir,"noisy")
        for folder in os.listdir(noisyPath):
            create_temporal_setup(TDScene,settings,folder)

        bpy.data.scenes.remove(TDScene)

        return {'FINISHED'}