import bpy
from bpy.types import NodeTree

from .. import SID_Settings
from ..create_denoiser import create_denoiser

def create_links_lc(sid_denoiser_tree: NodeTree, settings: SID_Settings) -> NodeTree:
    # Creates a super denoiser node group using the provided subgroup
    prefilter_quality = 'FAST' if settings.quality == 'STANDARD' else 'ACCURATE'

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
        input_node.outputs['Denoising Normal'],
        diffuse_denoiser_node.inputs['Denoising Normal']
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Albedo'],
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
        input_node.outputs['Denoising Albedo'],
        glossy_denoiser_node.inputs['Denoising Albedo']
        )


    ##TRANSMISSION##
    if settings.use_transmission:
        sid_tree.inputs.new("NodeSocketColor", "TransDir")
        transmission_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
        transmission_denoiser_node.node_tree = sid_denoiser_tree
        transmission_denoiser_node.location = (0, 200)
        transmission_denoiser_node.name = transmission_denoiser_node.label = "Denoise Transmission"

        # Link nodes
        sid_tree.links.new(
            input_node.outputs['TransDir'],
            transmission_denoiser_node.inputs['Direct']
            )
    if settings.use_caustics and settings.use_emission and settings.use_transmission:
        ##CAUSTICS##
        add_caustic = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_caustic.blend_type = "ADD"
        add_caustic.inputs[2].default_value = (0, 0, 0, 1)
        add_caustic.location = (1600, 600)
        add_caustic.name = add_caustic.label = "Add Caustics"

        sub_image_ddif = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        sub_image_ddif.blend_type = "SUBTRACT"
        sub_image_ddif.inputs[2].default_value = (0, 0, 0, 1)
        sub_image_ddif.location = (200, 1200)

        sub_image_idif = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        sub_image_idif.blend_type = "SUBTRACT"
        sub_image_idif.inputs[2].default_value = (0, 0, 0, 1)
        sub_image_idif.location = (400, 1100)

        sub_image_dgls = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        sub_image_dgls.blend_type = "SUBTRACT"
        sub_image_dgls.inputs[2].default_value = (0, 0, 0, 1)
        sub_image_dgls.location = (600, 1000)

        sub_image_igls = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        sub_image_igls.blend_type = "SUBTRACT"
        sub_image_igls.inputs[2].default_value = (0, 0, 0, 1)
        sub_image_igls.location = (800, 900)

        sub_image_emit = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        sub_image_emit.blend_type = "SUBTRACT"
        sub_image_emit.inputs[2].default_value = (0, 0, 0, 1)
        sub_image_emit.location = (1000, 800)

        sub_image_spec = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        sub_image_spec.blend_type = "SUBTRACT"
        sub_image_spec.inputs[2].default_value = (0, 0, 0, 1)
        sub_image_spec.location = (1200, 700)

        caustic_dn = create_denoiser(sid_tree, location=(1400, 500), prefilter_quality=prefilter_quality)

    ##VOLUMES##
    # Non existant in LuxCore, combined with diffuse

    if settings.use_emission:
        sid_tree.inputs.new("NodeSocketColor", "Emit")



    ##ADD IT ALL TOGETHER##
    add_diffuse_glossy = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    add_diffuse_glossy.blend_type = "ADD"
    add_diffuse_glossy.inputs[2].default_value = (0, 0, 0, 1)
    add_diffuse_glossy.location = (200, 500)
    add_diffuse_glossy.name = add_diffuse_glossy.label = "Add Glossy"

    if settings.use_transmission:
        add_trans = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_trans.blend_type = "ADD"
        add_trans.inputs[2].default_value = (0, 0, 0, 1)
        add_trans.location = (400, 400)
        add_trans.name = add_trans.label = "Add Transmission"

    if settings.use_emission:
        emission_dn = create_denoiser(sid_tree, "Denoise Emission", (600, 100), prefilter_quality)

        add_emission = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_emission.blend_type = "ADD"
        add_emission.inputs[2].default_value = (0, 0, 0, 1)
        add_emission.location = (800, 200)
        add_emission.name = add_emission.label = "Add Emission"

    alpha_dn = create_denoiser(sid_tree, "Denoise Alpha", (1200, -100), prefilter_quality)

    final_dn = create_denoiser(sid_tree, "Final Denoise", (1200, 100), prefilter_quality)

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

    if settings.use_transmission:
        sid_tree.links.new(
            prev_output,
            add_trans.inputs[1]
            )
        sid_tree.links.new(
            transmission_denoiser_node.outputs['Denoised Image'],
            add_trans.inputs[2]
            )
        prev_output = add_trans.outputs[0]

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

    #Caustics
    if settings.use_caustics and settings.use_emission and settings.use_transmission:
        sid_tree.links.new(
            input_node.outputs['Noisy Image'],
            sub_image_ddif.inputs[1]
            )
        sid_tree.links.new(
            input_node.outputs['DiffDir'],
            sub_image_ddif.inputs[2]
            )
        sid_tree.links.new(
            input_node.outputs['GlossDir'],
            sub_image_dgls.inputs[2]
            )
        sid_tree.links.new(
            input_node.outputs['DiffInd'],
            sub_image_idif.inputs[2]
            )
        sid_tree.links.new(
            input_node.outputs['GlossInd'],
            sub_image_igls.inputs[2]
            )
        sid_tree.links.new(
            input_node.outputs['TransDir'],
            sub_image_spec.inputs[2]
            )
        sid_tree.links.new(
            input_node.outputs['Emit'],
            sub_image_emit.inputs[2]
            )
        sid_tree.links.new(
            sub_image_ddif.outputs[0],
            sub_image_dgls.inputs[1]
            )
        sid_tree.links.new(
            sub_image_dgls.outputs[0],
            sub_image_idif.inputs[1]
            )
        sid_tree.links.new(
            sub_image_idif.outputs[0],
            sub_image_igls.inputs[1]
            )
        sid_tree.links.new(
            sub_image_igls.outputs[0],
            sub_image_emit.inputs[1]
            )
        sid_tree.links.new(
            sub_image_emit.outputs[0],
            sub_image_spec.inputs[1]
            )
        sid_tree.links.new(
            sub_image_spec.outputs[0],
            caustic_dn.inputs[0]
            )
        sid_tree.links.new(
            input_node.outputs['Denoising Normal'],
            caustic_dn.inputs[1]
            )
        sid_tree.links.new(
            input_node.outputs['Denoising Albedo'],
            caustic_dn.inputs[2]
            )
        sid_tree.links.new(
            caustic_dn.outputs[0],
            add_caustic.inputs[1]
            )
        sid_tree.links.new(
            add_emission.outputs[0],
            add_caustic.inputs[2]
            )
        
        prev_output = add_caustic.outputs[0]
        
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

    if settings.use_mlEXR:
        sid_tree.outputs.new("NodeSocketColor", "Denoised Diffuse")
        sid_tree.outputs.new("NodeSocketColor", "Denoised Glossy")

        if settings.use_transmission:
            sid_tree.outputs.new("NodeSocketColor", "Denoised Transmission")
            sid_tree.links.new(
                transmission_denoiser_node.outputs['Denoised Image'],
                output_node.inputs["Denoised Transmission"]
                )
        if settings.use_emission:
            sid_tree.outputs.new("NodeSocketColor", "Emission")
            sid_tree.links.new(
                emission_dn.outputs[0],
                output_node.inputs["Emission"]
                )
        if settings.use_caustics and settings.use_emission and settings.use_transmission:
            sid_tree.outputs.new("NodeSocketColor", "Denoised Caustics")
            sid_tree.links.new(
                caustic_dn.outputs[0],
                output_node.inputs["Denoised Caustics"]
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
