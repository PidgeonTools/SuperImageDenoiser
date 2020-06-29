<<<<<<< HEAD
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

def create_sid_denoiser_super():
    # Create SUPER quality dual denoiser node group
    SID_denoiser_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Denoiser.HQ")
    SID_denoiser_input_node = SID_denoiser_tree.nodes.new("NodeGroupInput")
    SID_denoiser_input_node.location = (-200, 0)

    SID_denoiser_output_node = SID_denoiser_tree.nodes.new("NodeGroupOutput")
    SID_denoiser_output_node.location = (600, 0)

    SID_denoiser_tree.inputs.new("NodeSocketColor", "Direct")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Indirect")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Color")
    SID_denoiser_tree.inputs.new("NodeSocketVector", "Denoising Normal")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
    SID_denoiser_tree.inputs['Color'].default_value = (1, 1, 1, 1)

    SID_denoiser_tree.outputs.new("NodeSocketColor", "Denoised Image")

    direct_dn = SID_denoiser_tree.nodes.new(type="CompositorNodeDenoise")
    direct_dn.location = (0, 200)
    indirect_dn = SID_denoiser_tree.nodes.new(type="CompositorNodeDenoise")
    indirect_dn.location = (0, 0)
    add_direct_indirect = SID_denoiser_tree.nodes.new(type="CompositorNodeMixRGB")
    add_direct_indirect.blend_type = "ADD"
    add_direct_indirect.location = (200, 200)
    mul_color = SID_denoiser_tree.nodes.new(type="CompositorNodeMixRGB")
    mul_color.blend_type = "MULTIPLY"
    mul_color.location = (400, 200)

    # Link nodes
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Direct'], direct_dn.inputs[0])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Normal'], direct_dn.inputs[1])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Albedo'], direct_dn.inputs[2])

    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Indirect'], indirect_dn.inputs[0])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Normal'], indirect_dn.inputs[1])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Albedo'], indirect_dn.inputs[2])

    SID_denoiser_tree.links.new(direct_dn.outputs[0], add_direct_indirect.inputs[1])
    SID_denoiser_tree.links.new(indirect_dn.outputs[0], add_direct_indirect.inputs[2])

    SID_denoiser_tree.links.new(add_direct_indirect.outputs[0], mul_color.inputs[1])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Color'], mul_color.inputs[2])

    SID_denoiser_tree.links.new(mul_color.outputs[0], SID_denoiser_output_node.inputs['Denoised Image'])

    return SID_denoiser_tree
=======
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
from SID_Settings import SID_Settings

def create_sid_denoiser_super():
    # Create SUPER quality dual denoiser node group
    SID_denoiser_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Denoiser.HQ")
    SID_denoiser_input_node = SID_denoiser_tree.nodes.new("NodeGroupInput")
    SID_denoiser_input_node.location = (-200, 0)

    SID_denoiser_output_node = SID_denoiser_tree.nodes.new("NodeGroupOutput")
    SID_denoiser_output_node.location = (600, 0)

    SID_denoiser_tree.inputs.new("NodeSocketColor", "Direct")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Indirect")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Color")
    SID_denoiser_tree.inputs.new("NodeSocketVector", "Denoising Normal")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
    SID_denoiser_tree.inputs['Color'].default_value = (1, 1, 1, 1)

    SID_denoiser_tree.outputs.new("NodeSocketColor", "Denoised Image")

    direct_dn = SID_denoiser_tree.nodes.new(type="CompositorNodeDenoise")
    direct_dn.location = (0, 200)
    indirect_dn = SID_denoiser_tree.nodes.new(type="CompositorNodeDenoise")
    indirect_dn.location = (0, 0)
    add_direct_indirect = SID_denoiser_tree.nodes.new(type="CompositorNodeMixRGB")
    add_direct_indirect.blend_type = "ADD"
    add_direct_indirect.location = (200, 200)
    mul_color = SID_denoiser_tree.nodes.new(type="CompositorNodeMixRGB")
    mul_color.blend_type = "MULTIPLY"
    mul_color.location = (400, 200)

    # Link nodes
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Direct'], direct_dn.inputs[0])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Normal'], direct_dn.inputs[1])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Albedo'], direct_dn.inputs[2])

    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Indirect'], indirect_dn.inputs[0])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Normal'], indirect_dn.inputs[1])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Albedo'], indirect_dn.inputs[2])

    SID_denoiser_tree.links.new(direct_dn.outputs[0], add_direct_indirect.inputs[1])
    SID_denoiser_tree.links.new(indirect_dn.outputs[0], add_direct_indirect.inputs[2])

    SID_denoiser_tree.links.new(add_direct_indirect.outputs[0], mul_color.inputs[1])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Color'], mul_color.inputs[2])

    SID_denoiser_tree.links.new(mul_color.outputs[0], SID_denoiser_output_node.inputs['Denoised Image'])

    return SID_denoiser_tree
>>>>>>> dc9e23cd6ac552f0b0ae285cb0a5bad03d5a1716
