from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
)

# Classes

class SID_Settings(PropertyGroup):
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
        default=False,
        description="Enable this if you have Transmissive materials in your scene"
        )

    use_volumetric: BoolProperty(
        name="Volume",
        default=False,
        description="Enable this if you have Volumetric materials in your scene"
        )

    compositor_reset: BoolProperty(
        name="CompositorReset",
        default=False,
        description="Resets the compositor when enabeling SID"
        )

    use_mlEXR: BoolProperty(
        name="MultiLayerEXR",
        default=False,
        description="Export a denoised MultiLayer EXR file"
        )
