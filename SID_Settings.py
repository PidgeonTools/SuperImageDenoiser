import bpy

from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty
)

# Classes

class SID_Settings(PropertyGroup):

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
                'Super (currently bugged)',
                "Highest denoiser quality (slower compositing time, uses significantly more memory)"
            ),
        ),
        default='HIGH',
        description="Choose the quality of the final denoised image. Affects memory usage and speed for compositing.",
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