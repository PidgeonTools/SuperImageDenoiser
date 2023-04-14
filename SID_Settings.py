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
                'SID TEMPORAL',
                'SID Temporal',
                'Temporal Animation Denoiser using Super Image Denoiser'
            ),
            (
                'TEMPORAL',
                'OptiX Temporal',
                'Temporal Animation Denoiser using OptiX'
            ),
        ),
        default='SID',
        description="Choose the denoiser type,\nSID is recomended for images and animations,\ntemporal for animations only",
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
    
    filename: StringProperty(
        name="File Name",
        default= "",
        description="File",
        subtype='DIR_PATH',
        maxlen=1024,
        options=set(), # Not animatable!
        )

    use_emission: BoolProperty(
        name="Emission",
        default=True,
        description="Enable this if you have emissive materials in your scene",
        options=set(), # Not animatable!
        )

    use_environment: BoolProperty(
        name="Environment",
        default=True,
        description="Enable this if your environment is visible in the render",
        options=set(), # Not animatable!
        )

    use_transmission: BoolProperty(
        name="Transmission",
        default=True,
        description="Enable this if you have transmissive materials in your scene",
        options=set(), # Not animatable!
        )

    use_volumetric: BoolProperty(
        name="Volume",
        default=False,
        description="Enable this if you have volumetric materials in your scene",
        options=set(), # Not animatable!
        )

    use_refraction: BoolProperty(
        name="Refraction",
        default=False,
        description="Enable this if you have refractive materials in your scene",
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
        description="Enable this if you have caustics in your Scene",
        options=set(), # Not animatable!
        )

    SIDT_MB_Toggle: BoolProperty(
        name="Motion Blur",
        default=True,
        description="Enables faked motion blur",
        options=set(), # Not animatable!
        )
    
    SIDT_MB_Samples: IntProperty(
        name="Samples",
        default=32,
        min=1,
        max=256,
        description="Number of motion blur samples,\nmore samples = more accurate motion blur",
        options=set(), # Not animatable!
        )
    
    SIDT_MB_Shutter: FloatProperty(
        name="Shutter Speed",
        default=0.5,
        min=0,
        max=2,
        description="Time taken in frames between shutter open and close",
        options=set(), # Not animatable!
        )
    
    SIDT_MB_Min: IntProperty(
        name="Min",
        default=0,
        min=0,
        max=1024,
        description="Minimum speed for a pixel to be blurred,\nused to separate fast moving objects from slow moving ones",
        options=set(), # Not animatable!
        )
    
    SIDT_MB_Max: IntProperty(
        name="Max",
        default=0,
        min=0,
        max=1024,
        description="Maximum speed, or zero for no limit",
        options=set(), # Not animatable!
        )
    
    SIDT_MB_Interpolation: BoolProperty(
        name="Curved Interpolation",
        default=False,
        description="Interpolate between frames in a bezier curve, rather than linearly",
        options=set(), # Not animatable!
        )
    
    SIDT_OUT_Compressed: BoolProperty(
        name="Smaller Working Files",
        default=False,
        description="Compresses the working files to save space,\nwill use 32bit EXR instead of 64bit",
        options=set(), # Not animatable!
        )
    
    SIDT_OUT_Preview: BoolProperty(
        name="Generate Preview Images",
        default=True,
        description="Saves preview images of the SID-Denoised frames,\nthese are not used by the temporal denoiser!\nThey are only used for previewing the rendered frames",
        options=set(), # Not animatable!
        )
        
    SIDT_OUT_Format: EnumProperty(
        name="File Output",
        items=(
            (
                'PNG',
                'PNG',
                "This is the slowest option\nsuiteable for final rendering.\nExports as 8bit RGBA PNG, 0% compression.\nWarning: no compression!"
            ),
            (
                'JPEG',
                'JPEG',
                "This is the smallest file size and fastest processing option.\nsuiteable for previewing.\nExports as RGB JPG, 90% quality.\nWarning: lossy compression, may cause JPEG artifacts!"
            ),
            (
                'OPEN_EXR',
                'EXR',
                "This is the highest quality option\nsuiteable if you want to edit the frames later.\nExports as 32bit RGBA EXR, zip compression.\nWarning: this will use a lot of disk space!"
            ),
        ),
        default='PNG',
        description="Choose the file format step 2 will output.",
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
