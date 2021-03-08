import bpy

from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty,
    StringProperty
)

# Classes

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
        default='SUPER',
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

    outputdir: StringProperty(
        name="Denoised Frames",
        default= "",
        description="Clean EXR Frames will be saved here",
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

    denoise_render_status: PointerProperty(
        type=SID_DenoiseRenderStatus,
        options=set(), # Not animatable!
        )
