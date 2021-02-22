import bpy

def create_sid_denoiser_super_lc():
    # Create SUPER quality dual denoiser node group
    sid_denoiser_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Denoiser.HQ")
    sid_denoiser_input_node = sid_denoiser_tree.nodes.new("NodeGroupInput")
    sid_denoiser_input_node.location = (-200, 0)

    sid_denoiser_output_node = sid_denoiser_tree.nodes.new("NodeGroupOutput")
    sid_denoiser_output_node.location = (600, 0)

    sid_denoiser_tree.inputs.new("NodeSocketColor", "Direct")
    sid_denoiser_tree.inputs.new("NodeSocketColor", "Indirect")
    sid_denoiser_tree.inputs.new("NodeSocketVector", "Denoising Normal")
    sid_denoiser_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
    sid_denoiser_tree.inputs['Indirect'].default_value = (0, 0, 0, 1)

    sid_denoiser_tree.outputs.new("NodeSocketColor", "Denoised Image")

    direct_dn = sid_denoiser_tree.nodes.new(type="CompositorNodeDenoise")
    direct_dn.location = (0, 200)
    indirect_dn = sid_denoiser_tree.nodes.new(type="CompositorNodeDenoise")
    indirect_dn.location = (0, 0)
    add_direct_indirect = sid_denoiser_tree.nodes.new(type="CompositorNodeMixRGB")
    add_direct_indirect.blend_type = "ADD"
    add_direct_indirect.location = (200, 200)

    # Link nodes
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Direct'],
        direct_dn.inputs[0]
        )
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Denoising Normal'],
        direct_dn.inputs[1]
        )
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Denoising Albedo'],
        direct_dn.inputs[2]
        )

    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Indirect'],
        indirect_dn.inputs[0]
        )
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Denoising Normal'],
        indirect_dn.inputs[1]
        )
    sid_denoiser_tree.links.new(
        sid_denoiser_input_node.outputs['Denoising Albedo'],
        indirect_dn.inputs[2]
        )

    sid_denoiser_tree.links.new(
        direct_dn.outputs[0],
        add_direct_indirect.inputs[1]
        )
    sid_denoiser_tree.links.new(
        indirect_dn.outputs[0],
        add_direct_indirect.inputs[2]
        )

    sid_denoiser_tree.links.new(
        add_direct_indirect.outputs[0],
        sid_denoiser_output_node.inputs['Denoised Image']
        )

    return sid_denoiser_tree
