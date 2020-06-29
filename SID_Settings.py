import bpy
from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty,
)

from SID_Create_DenoiserGroup import create_sid_super_denoiser_group
from SID_Create_Group import create_sid_super_group
from SID_QualityStandart import create_sid_denoiser_standard
from SID_QualityHigh import create_sid_denoiser_high
from SID_QualitySuper import create_sid_denoiser_super

# Classes

class SID_Settings(PropertyGroup):
    quality: EnumProperty(
        name="Denoiser Quality",
        items=(
            ('STANDARD', 'Standard', "Standard denoiser quality (fast compositing time, uses least memory)"),
            ('HIGH', 'High', "Extra denoiser quality (moderate compositing time, uses a little more memory)"),
            ('SUPER', 'Super', "Highest denoiser quality (slower compositing time, uses significantly more memory)"),
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