import bpy
from bpy.types import NodeTree

from . import SID_Settings
from .Cycles.SID_Create_Links_Cycles import create_links_cy

def create_sid_super_denoiser_group(sid_denoiser_tree: NodeTree, settings: SID_Settings):

    if settings.quality == "STANDARD":
        settings.SID_mlEXR = False 

    return create_links_cy(sid_denoiser_tree, settings)
