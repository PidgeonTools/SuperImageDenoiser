bl_info = {
    "name": "Super Image Denoiser (SID)",
    "author": "Kevin Lorengel, Chris Bond (Kamikaze)",
    "version": (2, 8),
    "blender": (2, 91, 0),
    "location": "Properties > Render > Create Super Denoiser",
    "description": "SID denoises your renders near-perfectly, with only one click!",
    "warning": "",
    "wiki_url": "https://discord.gg/cnFdGQP",
    "category": "Compositor",
}
import bpy
from bpy.props import (
    PointerProperty,
)
from .SuperImageDenoiser import SID_Create
from .SID_Create_DenoiserGroup import create_sid_super_denoiser_group
from .SID_Create_Group import create_sid_super_group

#Cycles
from .Cycles.SID_QualityHigh_Cycles import create_sid_denoiser_high_cy
from .Cycles.SID_QualitySuper_Cycles import create_sid_denoiser_super_cy
from .Cycles.SID_Create_Links_Cycles import create_links_cy
#Luxcore
from .LuxCore.SID_QualityHigh_LuxCore import create_sid_denoiser_high_lc
from .LuxCore.SID_QualitySuper_LuxCore import create_sid_denoiser_super_lc
from .LuxCore.SID_Create_Links_LuxCore import create_links_lc
#Octane
from .Octane.SID_QualityHigh_Octane import create_sid_denoiser_high_oc
from .Octane.SID_Create_Links_Octane import create_links_o

from .SID_Settings import SID_Settings
from .SID_Panel import SID_PT_Panel

from .SID_Temporal import TD_Render
from .SID_Temporal import TD_Denoise


# Register classes
classes = (
    SID_Settings,
    SID_PT_Panel,
    SID_Create,
    TD_Render,
    TD_Denoise
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
