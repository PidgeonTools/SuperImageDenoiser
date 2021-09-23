import bpy
from bpy.types import NodeTree
from .create_denoiser import create_denoiser

def create_sid_denoiser_standard() -> NodeTree:
    # Create standard quality denoiser node group
    prefilter_quality = 'FAST'

    sid_tree: NodeTree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SuperImageDenoiser")
    input_node = sid_tree.nodes.new("NodeGroupInput")
    input_node.location = (-200, 0)

    output_node = sid_tree.nodes.new("NodeGroupOutput")
    output_node.location = (800, 0)

    sid_tree.inputs.new("NodeSocketColor", "Noisy Image")
    sid_tree.inputs.new("NodeSocketVector", "Denoising Normal")
    sid_tree.inputs.new("NodeSocketColor", "Denoising Albedo")

    # Standard Denoiser
    standard_dn = create_denoiser(sid_tree, location=(0, 100), prefilter_quality=prefilter_quality)

    # Link nodes
    sid_tree.links.new(input_node.outputs['Noisy Image'], standard_dn.inputs[0])
    sid_tree.links.new(input_node.outputs['Denoising Normal'], standard_dn.inputs[1])
    sid_tree.links.new(input_node.outputs['Denoising Albedo'], standard_dn.inputs[2])

    sid_tree.outputs.new("NodeSocketColor", "Denoised Image")

    sid_tree.links.new(standard_dn.outputs[0], output_node.inputs["Denoised Image"])

    return sid_tree
