import bpy

from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty
)


def get_percent_complete(self):
    jobs_total = self['jobs_total']
    jobs_done = self['jobs_done']
    return 0 if jobs_total == 0 else 100 * jobs_done / jobs_total

def set_percent_complete(self, value):
    pass


class SID_DenoiseRenderStatus(PropertyGroup):
    is_rendering: BoolProperty(
        name="Rendering",
        description="Currently rendering",
        default=False,
        options=set(), # Not animatable!
        )

    should_stop: BoolProperty(
        name="Stop",
        description="User requested stop",
        default=False,
        options=set(), # Not animatable!
        )

    jobs_total: IntProperty(
        name="Total Jobs",
        description="Total number of jobs to run",
        options=set(), # Not animatable!
        )

    jobs_done: IntProperty(
        name="Jobs Done",
        description="Number of jobs completed",
        options=set(), # Not animatable!
        )

    jobs_remaining: IntProperty(
        name="Jobs Remaining",
        description="Number of jobs still remaining to complete",
        options=set(), # Not animatable!
        )

    percent_complete: FloatProperty(
        name="%",
        description="Percentage of jobs completed",
        subtype='PERCENTAGE',
        min=0,
        max=100,
        options=set(), # Not animatable!
        get=get_percent_complete,
        set=set_percent_complete,
        )


class SID_TemporalDenoiserStatus(PropertyGroup):
    is_running: BoolProperty(
        name="Denoising",
        description="A Denoising operation is currently in progress",
        default=False,
        options=set(), # Not animatable!
        )

    should_stop: BoolProperty(
        name="Stop",
        description="User requested stop",
        default=False,
        options=set(), # Not animatable!
        )

    jobs_total: IntProperty(
        name="Total Jobs",
        description="Total number of jobs to run",
        options=set(), # Not animatable!
        )

    jobs_done: IntProperty(
        name="Jobs Done",
        description="Number of jobs completed",
        options=set(), # Not animatable!
        )

    jobs_remaining: IntProperty(
        name="Jobs Remaining",
        description="Number of jobs still remaining to complete",
        options=set(), # Not animatable!
        )

    percent_complete: FloatProperty(
        name="%",
        description="Percentage of jobs completed",
        subtype='PERCENTAGE',
        min=0,
        max=100,
        options=set(), # Not animatable!
        get=get_percent_complete,
        set=set_percent_complete,
        )


class SID_Settings(PropertyGroup):

    denoiser_type: EnumProperty(
        name="Denoiser Type",
        items=(
            (
                'SID',
                'SID',
                'Super Image Denoiser'
            ),
            (
                'TEMPORAL',
                'Temporal',
                'Temporal Animation Denoiser'
            ),
        ),
        default='SID',
        description="Choose the denoiser type, SID is recomended for images, Temporal for animations only",
        options=set(), # Not animatable!
        )

    quality: EnumProperty(
        name="Denoiser Quality",
        items=(
            (
                'STANDARD',
                'Standard',
                "Standard denoiser quality (fast compositing time, uses least memory)"
            ),
            (
                'HIGH',
                'High',
                "Extra denoiser quality (moderate compositing time, uses a little more memory)"
            ),
            (
                'SUPER',
                'Super',
                "Highest denoiser quality (slower compositing time, uses significantly more memory)"
            ),
        ),
        default='HIGH',
        description="Choose the quality of the final denoised image. Affects memory usage and speed for compositing.",
        options=set(), # Not animatable!
        )

    inputdir: StringProperty(
        name="Noisy Frames",
        default= "",
        description="Noisy EXR Frames will be saved here",
        subtype='DIR_PATH',
        maxlen=1024,
        options=set(), # Not animatable!
        )

    use_emission: BoolProperty(
        name="Emission",
        default=True,
        description="Enable this if you have Emissive materials in your scene",
        options=set(), # Not animatable!
        )

    use_environment: BoolProperty(
        name="Environment",
        default=True,
        description="Enable this if you have Environment materials in your scene",
        options=set(), # Not animatable!
        )

    use_transmission: BoolProperty(
        name="Transmission",
        default=True,
        description="Enable this if you have Transmissive materials in your scene",
        options=set(), # Not animatable!
        )

    use_volumetric: BoolProperty(
        name="Volume",
        default=False,
        description="Enable this if you have Volumetric materials in your scene",
        options=set(), # Not animatable!
        )

    use_refraction: BoolProperty(
        name="Refraction",
        default=False,
        description="Enable this if you have Refractive materials in your scene",
        options=set(), # Not animatable!
        )

    use_sss: BoolProperty(
        name="SSS",
        default=False,
        description="Enable this if you have SSS materials in your scene",
        options=set(), # Not animatable!
        )

    compositor_reset: BoolProperty(
        name="CompositorReset",
        default=True,
        description="Refreshes SID instead of adding another node group",
        options=set(), # Not animatable!
        )

    use_mlEXR: BoolProperty(
        name="MultiLayerEXR",
        default=False,
        description="Export a denoised MultiLayer EXR file",
        options=set(), # Not animatable!
        )

    use_caustics: BoolProperty(
        name="Caustics",
        default=True,
        description="Enable this if you have Caustics in your Scene",
        options=set(), # Not animatable!
        )

    # Temporal denoiser part 1: render noisy frames
    denoise_render_status: PointerProperty(
        type=SID_DenoiseRenderStatus,
        options=set(), # Not animatable!
        )

    # Temporal denoiser part 2: denoise animation
    temporal_denoiser_status: PointerProperty(
        type=SID_TemporalDenoiserStatus,
        options=set(), # Not animatable!
        )
