import bpy
from bpy.types import NodeTree

def create_sid_denoiser_high_oc() -> NodeTree:
    # Create high quality dual denoiser node group
    sid_denoiser_tree: NodeTree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Denoiser.HQ")
    sid_denoiser_input_node = sid_denoiser_tree.nodes.new("NodeGroupInput")
    sid_denoiser_input_node.location = (-200, 0)

    sid_denoiser_output_node = sid_denoiser_tree.nodes.new("NodeGroupOutput")
    sid_denoiser_output_node.location = (600, 0)

    sid_denoiser_tree.inputs.new("NodeSocketColor", "Direct")
    sid_denoiser_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
    sid_denoiser_tree.inputs.new("NodeSocketColor", "Denoising Normal")

    sid_denoiser_tree.outputs.new("NodeSocketColor", "Denoised Image")

    dn_node = sid_denoiser_tree.nodes.new(type="CompositorNodeDenoise")
    dn_node.location = (400, 100)

    # Link nodes

    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Direct'],
        dn_node.inputs[0]
        )
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Denoising Normal'],
        dn_node.inputs[2]
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
