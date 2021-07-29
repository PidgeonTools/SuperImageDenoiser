import bpy
from bpy.types import NodeTree

from .. import SID_Settings

def create_links_rm(sid_denoiser_tree: NodeTree, settings: SID_Settings) -> NodeTree:

    # Creates a super denoiser node group using the provided subgroup
    scene = bpy.context.scene

    sid_tree: NodeTree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SuperImageDenoiser")
    input_node = sid_tree.nodes.new("NodeGroupInput")
    input_node.location = (-200, 0)

    output_node = sid_tree.nodes.new("NodeGroupOutput")
    output_node.location = (1800, 0)

    sid_tree.inputs.new("NodeSocketColor", "Noisy Image")
    sid_tree.inputs.new("NodeSocketVector", "Denoising Normal")
    sid_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
    sid_tree.inputs.new("NodeSocketColor", "Alpha")

    # Add instances of the dual denoiser

    ##DIFFUSE##
    sid_tree.inputs.new("NodeSocketColor", "DiffDir")
    sid_tree.inputs.new("NodeSocketColor", "DiffInd")
    sid_tree.inputs.new("NodeSocketColor", "DiffCol")
    diffuse_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
    diffuse_denoiser_node.node_tree = sid_denoiser_tree
    diffuse_denoiser_node.location = (0, 600)
    diffuse_denoiser_node.name = diffuse_denoiser_node.label = "Denoise Diffuse"

    # link nodes
    sid_tree.links.new(
        input_node.outputs['DiffDir'],
        diffuse_denoiser_node.inputs['Direct']
        )
    sid_tree.links.new(
        input_node.outputs['DiffInd'],
        diffuse_denoiser_node.inputs['Indirect']
        )
    sid_tree.links.new(
        input_node.outputs['DiffCol'],
        diffuse_denoiser_node.inputs['Color']
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Normal'],
        diffuse_denoiser_node.inputs['Denoising Normal']
        )
    sid_tree.links.new(
        input_node.outputs['DiffCol'],
        diffuse_denoiser_node.inputs['Denoising Albedo']
        )


    ##GLOSSY##
    sid_tree.inputs.new("NodeSocketColor", "GlossDir")
    sid_tree.inputs.new("NodeSocketColor", "GlossInd")
    glossy_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
    glossy_denoiser_node.node_tree = sid_denoiser_tree
    glossy_denoiser_node.location = (0, 400)
    glossy_denoiser_node.name = glossy_denoiser_node.label = "Denoise Glossy"

    # Link nodes
    sid_tree.links.new(
        input_node.outputs['GlossDir'],
        glossy_denoiser_node.inputs['Direct']
        )
    sid_tree.links.new(
        input_node.outputs['GlossInd'],
        glossy_denoiser_node.inputs['Indirect']
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Normal'],
        glossy_denoiser_node.inputs['Denoising Normal']
        )
    sid_tree.links.new(
        input_node.outputs['DiffCol'],
        glossy_denoiser_node.inputs['Denoising Albedo']
        )

    if settings.use_emission:
        sid_tree.inputs.new("NodeSocketColor", "Emit")

    if settings.use_sss:
        sid_tree.inputs.new("NodeSocketColor", "SubsurfaceInd")

    ##ADD IT ALL TOGETHER##
    add_diffuse_glossy = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    add_diffuse_glossy.blend_type = "ADD"
    add_diffuse_glossy.inputs[2].default_value = (0, 0, 0, 1)
    add_diffuse_glossy.location = (200, 500)
    add_diffuse_glossy.name = add_diffuse_glossy.label = "Add Glossy"

    if settings.use_emission:
        emission_dn = sid_tree.nodes.new(type="CompositorNodeDenoise")
        emission_dn.location = (600, 100)
        emission_dn.name = emission_dn.label = "Denoise Emission"

        add_emission = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_emission.blend_type = "ADD"
        add_emission.inputs[2].default_value = (0, 0, 0, 1)
        add_emission.location = (800, 200)
        add_emission.name = add_emission.label = "Add Emission"

    if settings.use_sss:
        sss_dn = sid_tree.nodes.new(type="CompositorNodeDenoise")
        sss_dn.location = (600, 300)
        sss_dn.name = sss_dn.label = "Denoise SSS"

        add_sss = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_sss.blend_type = "ADD"
        add_sss.inputs[2].default_value = (0, 0, 0, 1)
        add_sss.location = (800, 500)
        add_sss.name = add_sss.label = "Add SSS"

    alpha_dn = sid_tree.nodes.new(type="CompositorNodeDenoise")
    alpha_dn.location = (1200, -100)
    alpha_dn.name = alpha_dn.label = "Denoise Alpha"

    final_dn = sid_tree.nodes.new(type="CompositorNodeDenoise")
    final_dn.location = (1200, 100)
    final_dn.name = final_dn.label = "Final Denoise"

    seperate_node = sid_tree.nodes.new(type="CompositorNodeSepRGBA")
    seperate_node.location = (1400, 100)
    combine_node = sid_tree.nodes.new(type="CompositorNodeCombRGBA")
    combine_node.location = (1600, 100)

    # Link nodes
    sid_tree.links.new(
        diffuse_denoiser_node.outputs['Denoised Image'],
        add_diffuse_glossy.inputs[1]
        )
    sid_tree.links.new(
        glossy_denoiser_node.outputs['Denoised Image'],
        add_diffuse_glossy.inputs[2]
        )
    prev_output = add_diffuse_glossy.outputs[0]

    if settings.use_emission:
        sid_tree.links.new(
            prev_output,
            add_emission.inputs[1]
            )
        sid_tree.links.new(
            input_node.outputs['Emit'],
            emission_dn.inputs[0]
            )
        sid_tree.links.new(
            emission_dn.outputs[0],
            add_emission.inputs[2]
            )
        prev_output = add_emission.outputs[0]

    if settings.use_sss:
        sid_tree.links.new(
            prev_output,
            add_sss.inputs[1]
            )
        sid_tree.links.new(
            input_node.outputs['SubsurfaceInd'],
            sss_dn.inputs[0]
            )
        sid_tree.links.new(
            sss_dn.outputs[0],
            add_sss.inputs[2]
            )
        prev_output = add_sss.outputs[0]

    sid_tree.links.new(
        prev_output,
        final_dn.inputs[0]
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Normal'],
        final_dn.inputs[1]
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Albedo'],
        final_dn.inputs[2]
        )
    sid_tree.links.new(
        input_node.outputs['Alpha'],
        alpha_dn.inputs[0]
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Normal'],
        alpha_dn.inputs[1]
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Albedo'],
        alpha_dn.inputs[2]
        )

    sid_tree.outputs.new("NodeSocketColor", "Denoised Image")

    sid_tree.outputs.new("NodeSocketColor", "Denoised Diffuse")
    sid_tree.outputs.new("NodeSocketColor", "Denoised Glossy")

    if settings.use_emission:
        sid_tree.outputs.new("NodeSocketColor", "Emission")
        sid_tree.links.new(
            emission_dn.outputs[0],
            output_node.inputs["Emission"]
            )
            
    if settings.use_sss:
        sid_tree.outputs.new("NodeSocketColor", "SubsurfaceInd")
        sid_tree.links.new(
            sss_dn.outputs[0],
            output_node.inputs["SubsurfaceInd"]
            )
            
    sid_tree.links.new(
        diffuse_denoiser_node.outputs['Denoised Image'],
        output_node.inputs['Denoised Diffuse']
        )
    sid_tree.links.new(
        glossy_denoiser_node.outputs['Denoised Image'],
        output_node.inputs['Denoised Glossy']
        )

    sid_tree.links.new(
        combine_node.outputs[0],
        output_node.inputs["Denoised Image"]
        )
    sid_tree.links.new(
        seperate_node.outputs["R"],
        combine_node.inputs["R"]
        )
    sid_tree.links.new(
        seperate_node.outputs["G"],
        combine_node.inputs["G"]
        )
    sid_tree.links.new(
        seperate_node.outputs["B"],
        combine_node.inputs["B"]
        )
    sid_tree.links.new(
        alpha_dn.outputs[0],
        combine_node.inputs["A"]
        )
    sid_tree.links.new(
        final_dn.outputs[0],
        seperate_node.inputs[0]
        )  
    return sid_tree
