bl_info = {
    "name": "Super Image Denoiser (SID)",
    "author": "Kevin Lorengel, Chris Bond (Kamikaze)",
    "version": (3, 2, 0),
    "blender": (2, 83, 0),
    "location": "Properties > Render > Create Super Denoiser",
    "description": "SID denoises your renders near-perfectly, with only one click!",
    "warning": "",
    "wiki_url": "https://discord.gg/cnFdGQP",
    "endpoint_url": "https://raw.githubusercontent.com/PidgeonTools/SAM-Endpoints/main/SuperImageDenoiser.json",
    "tracker_url": "https://github.com/PidgeonTools/SuperImageDenoiser/issues",
    "category": "Compositor",
}
import bpy
from bpy.app.handlers import persistent
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
#Renderman
from .Renderman.SID_QualityHigh_Renderman import create_sid_denoiser_high_rm
from .Renderman.SID_Create_Links_Renderman import create_links_rm

from .SID_Settings import SID_DenoiseRenderStatus, SID_Settings, SID_TemporalDenoiserStatus
from .SID_Panel import SID_PT_SID_Panel, SID_PT_SOCIALS_Panel

from .SID_Temporal import (
    TD_OT_Render,
    TD_OT_StopRender,
    TD_OT_Denoise,
    TD_OT_StopDenoise,
    )

from . import addon_updater_ops

class DemoPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # addon updater preferences

    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=True,
    )
    updater_intrval_months: bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days: bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31
    )
    updater_intrval_hours: bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes: bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout
        # col = layout.column() # works best if a column, or even just self.layout
        mainrow = layout.row()
        col = mainrow.column()

        # updater draw function
        # could also pass in col as third arg
        addon_updater_ops.update_settings_ui(self, context)

        # Alternate draw function, which is more condensed and can be
        # placed within an existing draw function. Only contains:
        #   1) check for update/update now buttons
        #   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

        # Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # col.operator("wm.url_open","Open webpage ").url=addon_updater_ops.updater.website


classes = (
    SID_DenoiseRenderStatus,
    SID_TemporalDenoiserStatus,
    SID_Settings,
    SID_PT_SID_Panel,
    SID_PT_SOCIALS_Panel,
    SID_Create,
    TD_OT_Render,
    TD_OT_StopRender,
    TD_OT_Denoise,
    TD_OT_StopDenoise,
    DemoPreferences
)


@persistent
def load_handler(dummy):
    try:
        bpy.context.scene.sid_settings.denoise_render_status.is_rendering = False
    except:
        pass

    try:
        bpy.context.scene.sid_settings.temporal_denoiser_status.is_denoising = False
    except:
        pass


def register():
    # addon updater code and configurations
    # in case of broken version, try to register the updater first
    # so that users can revert back to a working version
    addon_updater_ops.register(bl_info)

    # register the example panel, to show updater buttons
    for cls in classes:
        addon_updater_ops.make_annotations(cls)  # to avoid blender 2.8 warnings
        bpy.utils.register_class(cls)

    bpy.types.Scene.sid_settings = PointerProperty(type=SID_Settings, options=set())

    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    # addon updater unregister
    addon_updater_ops.unregister()

    # register the example panel, to show updater buttons

    from bpy.utils import unregister_class

    del bpy.types.Scene.sid_settings

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
