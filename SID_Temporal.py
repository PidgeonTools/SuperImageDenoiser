import bpy
import os 
import glob
from bpy.types import Operator
from .SID_Settings import SID_Settings
from typing import NamedTuple


# disable uneeded passes for better performance

class SavedRenderSettings(NamedTuple):
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
    old_pass_co: bool
    old_pass_cm: bool
    old_pass_ca: bool
    old_file_format: str
    old_compositor: bool
    old_sequencer: bool
    old_path: bool
    old_usedenoise: bool
    old_denoiser: str

def save_render_settings(context,view_layer):
    scene = context.scene
    render = scene.render
    return SavedRenderSettings(
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
        old_pass_co = view_layer.cycles.use_pass_crypto_object,
        old_pass_cm = view_layer.cycles.use_pass_crypto_material,
        old_pass_ca = view_layer.cycles.use_pass_crypto_asset,
        old_file_format = render.image_settings.file_format,
        old_compositor = scene.render.use_compositing,
        old_sequencer = scene.render.use_sequencer,
        old_path = scene.render.filepath,
        old_usedenoise = scene.cycles.use_denoising,
        old_denoiser = scene.cycles.denoiser



    )

def restore_render_settings(context, savedsettings: SavedRenderSettings, view_layer):
    scene = context.scene
    cam = scene.camera
    render = scene.render

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
    view_layer.cycles.use_pass_crypto_object = savedsettings.old_pass_co
    view_layer.cycles.use_pass_crypto_material = savedsettings.old_pass_cm
    view_layer.cycles.use_pass_crypto_asset = savedsettings.old_pass_ca
    render.image_settings.file_format = savedsettings.old_file_format
    scene.render.use_compositing = savedsettings.old_compositor
    scene.render.use_sequencer = savedsettings.old_compositor
    scene.render.filepath = savedsettings.old_path
    scene.cycles.use_denoising = savedsettings.old_usedenoise
    scene.cycles.denoiser = savedsettings.old_denoiser

class TD_Render(Operator):

    bl_idname = "object.temporaldenoise_render"
    bl_label = "Render Noisy Frames 1/2"
    bl_description = "Renders the Noisy images with the correct settings, step 1 of 2"

    def execute(
            self,
            context,
            ):
        scene = context.scene
        settings: SID_Settings = scene.sid_settings

        animStart = scene.frame_start
        animEnd = scene.frame_end
        
        saved_settings = None
        LayerCounter = 0
        for view_layer in scene.view_layers:

            LayerCounter += 1

            if not view_layer.use:
                continue

            ####save###
            self.saved_settings = save_render_settings(context, view_layer)

            ###change###
            #image
            scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
            scene.render.image_settings.color_mode = 'RGBA'
            scene.render.image_settings.color_depth = '32'
            scene.render.image_settings.exr_codec = 'ZIP'
            #passes
            view_layer.use_pass_combined = True
            view_layer.use_pass_z = False
            view_layer.use_pass_mist = False
            view_layer.use_pass_normal = False
            view_layer.use_pass_vector = False
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
            view_layer.cycles.use_pass_crypto_object = False
            view_layer.cycles.use_pass_crypto_material = False
            view_layer.cycles.use_pass_crypto_asset = False
            bpy.context.scene.render.use_compositing = False
            bpy.context.scene.render.use_sequencer = False



            for frame in range(animStart,animEnd + 1):
                scene.frame_set( frame ) # Set frame

                fileName = str(LayerCounter) + str(frame).zfill(5) # Formats 5 --> 00005
                fileName += scene.render.file_extension
                fileName = settings.inputdir + fileName
                scene.render.filepath = fileName

                print(fileName)

                bpy.ops.render.render(write_still = True)

            ####restore####
            restore_render_settings(context, self.saved_settings , view_layer)

        return {'FINISHED'}

class TD_Denoise(Operator):

    bl_idname = "object.temporaldenoise_denoise"
    bl_label = "Denoise Noisy Frames 2/2"
    bl_description = "Denoises Noisy Frames, step 2 of 2"

    #remember settings


    def execute(
            self,
            context,
            ):

        scene = context.scene
        settings: SID_Settings = scene.sid_settings
        view_layer = context.view_layer

        ####denoise###

        ####save###
        self.saved_settings = save_render_settings(context, view_layer)

        ###change###
        #denoiser
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = 'NLM'

        os.chdir(settings.inputdir)
        myfiles=(glob.glob("*.exr"))
        for file in myfiles:
            print(settings.inputdir + file + " to " + settings.outputdir + file)
            bpy.ops.cycles.denoise_animation(input_filepath=(settings.inputdir + file), output_filepath=(settings.outputdir + file))

        ####restore####
        restore_render_settings(context, self.saved_settings , view_layer)

        return {'FINISHED'}