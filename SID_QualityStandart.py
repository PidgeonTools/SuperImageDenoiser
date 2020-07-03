import bpy

def create_sid_denoiser_standard():
    # Create standard quality denoiser node group

    SID_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SuperImageDenoiser")
    input_node = SID_tree.nodes.new("NodeGroupInput")
    input_node.location = (-200, 0)

    output_node = SID_tree.nodes.new("NodeGroupOutput")
    output_node.location = (800, 0)

    SID_tree.inputs.new("NodeSocketColor", "Noisy Image")
    SID_tree.inputs.new("NodeSocketVector", "Denoising Normal")
    SID_tree.inputs.new("NodeSocketColor", "Denoising Albedo")

    # Standard Denoiser
    standard_dn = SID_tree.nodes.new(type="CompositorNodeDenoise")
    standard_dn.location = (0, 100)
    
    # Link nodes
    SID_tree.links.new(input_node.outputs['Noisy Image'], standard_dn.inputs[0])
    SID_tree.links.new(input_node.outputs['Denoising Normal'], standard_dn.inputs[1])
    SID_tree.links.new(input_node.outputs['Denoising Albedo'], standard_dn.inputs[2])

    SID_tree.outputs.new("NodeSocketColor", "Denoised Image")

    SID_tree.links.new(standard_dn.outputs[0], output_node.inputs["Denoised Image"])

    return SID_tree