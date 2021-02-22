import bpy

from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty
)

# Classes

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
        description="Choose the denoiser type, SID is recomended for images, Temporal for animations only"
    )

    quality: EnumProperty(
        name="Denoiser Quality",
        items=(
#            (
#                'INTERNAL NAME'
#                'external name'
#                'fancy description'
#            )
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
        description="Choose the quality of the final denoised image. Affects memory usage and speed for compositing."
    )

    inputdir: StringProperty(
        name="Noisy Frames",
        default= "",
        description="Noisy EXR Frames will be saved here",
        subtype='DIR_PATH',
        maxlen=1024
        )

    outputdir: StringProperty(
        name="Denoised Frames",
        default= "",
        description="Clean EXR Frames will be saved here",
        subtype='DIR_PATH',
        maxlen=1024
        )

    use_emission: BoolProperty(
        name="Emission",
        default=True,
        description="Enable this if you have Emissive materials in your scene"
        )

    use_environment: BoolProperty(
        name="Environment",
        default=True,
        description="Enable this if you have Environment materials in your scene"
        )

    use_transmission: BoolProperty(
        name="Transmission",
        default=True,
        description="Enable this if you have Transmissive materials in your scene"
        )

    use_volumetric: BoolProperty(
        name="Volume",
        default=False,
        description="Enable this if you have Volumetric materials in your scene"
        )

    use_refraction: BoolProperty(
        name="Refraction",
        default=False,
        description="Enable this if you have Refractive materials in your scene"
        )

    use_sss: BoolProperty(
        name="SSS",
        default=False,
        description="Enable this if you have SSS materials in your scene"
        )

    compositor_reset: BoolProperty(
        name="CompositorReset",
        default=True,
        description="Refreshes SID instead of adding another node group"
        )

    use_mlEXR: BoolProperty(
        name="MultiLayerEXR",
        default=False,
        description="Export a denoised MultiLayer EXR file"
        )

    use_caustics: BoolProperty(
        name="Caustics",
        default=True,
        description="Enable this if you have Caustics in your Scene"
        )
