import bpy
from bpy.types import NodeTree
from ..create_denoiser import create_denoiser

def create_sid_denoiser_high_rm() -> NodeTree:
    # Create high quality dual denoiser node group
    prefilter_quality = 'ACCURATE'

    sid_denoiser_tree: NodeTree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Denoiser.HQ")
    sid_denoiser_input_node = sid_denoiser_tree.nodes.new("NodeGroupInput")
    sid_denoiser_input_node.location = (-200, 0)

    sid_denoiser_output_node = sid_denoiser_tree.nodes.new("NodeGroupOutput")
    sid_denoiser_output_node.location = (600, 0)

    sid_denoiser_tree.inputs.new("NodeSocketColor", "Direct")
    sid_denoiser_tree.inputs.new("NodeSocketColor", "Indirect")
    sid_denoiser_tree.inputs.new("NodeSocketColor", "Color")
    sid_denoiser_tree.inputs.new("NodeSocketVector", "Denoising Normal")
    sid_denoiser_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
    sid_denoiser_tree.inputs['Color'].default_value = (1, 1, 1, 1)

    sid_denoiser_tree.outputs.new("NodeSocketColor", "Denoised Image")

    add_direct_indirect = sid_denoiser_tree.nodes.new(type="CompositorNodeMixRGB")
    add_direct_indirect.blend_type = "ADD"
    add_direct_indirect.inputs[2].default_value = (1, 1, 1, 1)
    add_direct_indirect.location = (0, 100)
    mul_color = sid_denoiser_tree.nodes.new(type="CompositorNodeMixRGB")
    mul_color.blend_type = "MULTIPLY"
    mul_color.location = (200, 100)
    dn_node = create_denoiser(sid_denoiser_tree, location=(400, 100), prefilter_quality=prefilter_quality)

    # Link nodes
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Direct'],
        add_direct_indirect.inputs[1]
        )
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Indirect'],
        add_direct_indirect.inputs[2]
        )
    sid_denoiser_tree.links.new(
        add_direct_indirect.outputs[0],
        mul_color.inputs[1]
        )
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Color'],
        mul_color.inputs[2]
        )
    sid_denoiser_tree.links.new(
        mul_color.outputs[0],
        dn_node.inputs[0]
        )
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Denoising Normal'],
        dn_node.inputs[1]
        )
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Denoising Albedo'],
        dn_node.inputs[2]
        )
    sid_denoiser_tree.links.new(
        dn_node.outputs[0],
        sid_denoiser_output_node.inputs['Denoised Image']
        )

    return sid_denoiser_tree
