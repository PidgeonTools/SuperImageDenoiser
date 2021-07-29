import bpy

from . import SID_Settings

from .Cycles.SID_Create_Group_Cycles import create_cycles_group
from .LuxCore.SID_Create_Group_LuxCore import create_LuxCore_group
from .Octane.SID_Create_Group_Octane import create_Octane_group
from .Renderman.SID_Create_Group_Renderman import create_renderman_group

def create_sid_super_group(
        standard_denoiser_tree,
        high_denoiser_tree,
        super_denoiser_tree,
        settings: SID_Settings,
        ):

    RenderEngine = bpy.context.scene.render.engine

    ##############
    ### CYCLES ###
    ##############
    if RenderEngine == 'CYCLES':
        sid_super_group = create_cycles_group(standard_denoiser_tree,high_denoiser_tree,super_denoiser_tree,settings)

    ###############
    ### LUXCORE ###
    ###############
    if RenderEngine == 'LUXCORE':
        sid_super_group = create_LuxCore_group(standard_denoiser_tree,high_denoiser_tree,super_denoiser_tree,settings)

    ##############
    ### OCTANE ###
    ##############
    if RenderEngine == 'octane':
        sid_super_group = create_Octane_group(standard_denoiser_tree,high_denoiser_tree,super_denoiser_tree,settings)
        
    #################
    ### RENDERMAN ###
    #################
    if RenderEngine == 'PRMAN_RENDER':
        sid_super_group = create_renderman_group(standard_denoiser_tree,high_denoiser_tree,super_denoiser_tree,settings)
        

    return sid_super_group
