import bpy
from bpy.types import NodeTree

from .. import SID_Settings
from ..create_denoiser import create_denoiser

def create_links_o(sid_denoiser_tree: NodeTree, settings: SID_Settings) -> NodeTree:

    # Creates a super denoiser node group using the provided subgroup
    prefilter_quality = 'FAST' if settings.quality == 'STANDARD' else 'ACCURATE'

    sid_tree: NodeTree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SuperImageDenoiser")
    input_node = sid_tree.nodes.new("NodeGroupInput")
    input_node.location = (-200, 0)

    output_node = sid_tree.nodes.new("NodeGroupOutput")
    output_node.location = (2600, 0)

    sid_tree.inputs.new("NodeSocketColor", "Noisy Image")
    sid_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
    sid_tree.inputs.new("NodeSocketColor", "Denoising Normal")
    sid_tree.inputs.new("NodeSocketColor", "Alpha")

    # Add instances of the dual denoiser

    ##DIFFUSE##
    sid_tree.inputs.new("NodeSocketColor", "Diffuse")
    diffuse_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
    diffuse_denoiser_node.node_tree = sid_denoiser_tree
    diffuse_denoiser_node.location = (0, 900)
    diffuse_denoiser_node.name = diffuse_denoiser_node.label = "Denoise Diffuse"

    # link nodes
    sid_tree.links.new(
        input_node.outputs['Diffuse'],
        diffuse_denoiser_node.inputs['Direct']
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Albedo'],
        diffuse_denoiser_node.inputs['Denoising Albedo']
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Normal'],
        diffuse_denoiser_node.inputs['Denoising Normal']
        )

    ##REFLECTION##
    sid_tree.inputs.new("NodeSocketColor", "Reflection")
    reflection_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
    reflection_denoiser_node.node_tree = sid_denoiser_tree
    reflection_denoiser_node.location = (0, 700)
    reflection_denoiser_node.name = reflection_denoiser_node.label = "Denoise Reflection"

    # Link nodes
    sid_tree.links.new(
        input_node.outputs['Reflection'],
        reflection_denoiser_node.inputs['Direct']
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Albedo'],
        reflection_denoiser_node.inputs['Denoising Albedo']
        )
    sid_tree.links.new(
        input_node.outputs['Denoising Normal'],
        reflection_denoiser_node.inputs['Denoising Normal']
        )

    ##REFRACTION##
    if settings.use_refraction:
        sid_tree.inputs.new("NodeSocketColor", "Refraction")
        refraction_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
        refraction_denoiser_node.node_tree = sid_denoiser_tree
        refraction_denoiser_node.location = (0, 500)
        refraction_denoiser_node.name = refraction_denoiser_node.label = "Denoise Refraction"

        # Link nodes
        sid_tree.links.new(
            input_node.outputs['Refraction'],
            refraction_denoiser_node.inputs['Direct']
            )
        sid_tree.links.new(
            input_node.outputs['Denoising Albedo'],
            refraction_denoiser_node.inputs['Denoising Albedo']
            )
        sid_tree.links.new(
            input_node.outputs['Denoising Normal'],
            refraction_denoiser_node.inputs['Denoising Normal']
            )

    ##TRANSMISSION##
    if settings.use_transmission:
        sid_tree.inputs.new("NodeSocketColor", "Transmission")
        transmission_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
        transmission_denoiser_node.node_tree = sid_denoiser_tree
        transmission_denoiser_node.location = (0, 300)
        transmission_denoiser_node.name = transmission_denoiser_node.label = "Denoise Transmission"

        # Link nodes
        sid_tree.links.new(
            input_node.outputs['Transmission'],
            transmission_denoiser_node.inputs['Direct']
            )
        sid_tree.links.new(
            input_node.outputs['Denoising Albedo'],
            transmission_denoiser_node.inputs['Denoising Albedo']
            )
        sid_tree.links.new(
            input_node.outputs['Denoising Normal'],
            transmission_denoiser_node.inputs['Denoising Normal']
            )
    ##SSS##
    if settings.use_sss:
        sid_tree.inputs.new("NodeSocketColor", "SSS")
        sss_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
        sss_denoiser_node.node_tree = sid_denoiser_tree
        sss_denoiser_node.location = (0, 100)
        sss_denoiser_node.name = sss_denoiser_node.label = "Denoise SSS"

        # Link nodes
        sid_tree.links.new(
            input_node.outputs['SSS'],
            sss_denoiser_node.inputs['Direct']
            )
        sid_tree.links.new(
            input_node.outputs['Denoising Albedo'],
            sss_denoiser_node.inputs['Denoising Albedo']
            )
        sid_tree.links.new(
            input_node.outputs['Denoising Normal'],
            sss_denoiser_node.inputs['Denoising Normal']
            )

    ##VOLUMES##
    if settings.use_volumetric:
        sid_tree.inputs.new("NodeSocketColor", "Volume")
        volume_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
        volume_denoiser_node.node_tree = sid_denoiser_tree
        volume_denoiser_node.location = (0, -100)
        volume_denoiser_node.name = volume_denoiser_node.label = "Denoise Volume"

        # Link nodes
        sid_tree.links.new(
            input_node.outputs['Volume'],
            volume_denoiser_node.inputs['Direct']
            )

        sid_tree.inputs.new("NodeSocketColor", "VolumeEmission")
        volume_e_denoiser_node = sid_tree.nodes.new("CompositorNodeGroup")
        volume_e_denoiser_node.node_tree = sid_denoiser_tree
        volume_e_denoiser_node.location = (0, -300)
        volume_e_denoiser_node.name = volume_e_denoiser_node.label = "Denoise Volume Emission"

        # Link nodes
        sid_tree.links.new(
            input_node.outputs['VolumeEmission'],
            volume_e_denoiser_node.inputs['Direct']
            )

    if settings.use_emission:
        sid_tree.inputs.new("NodeSocketColor", "Emission")
        emission_dn = create_denoiser(sid_tree, "Denoise Emission", (0, -500), prefilter_quality)

    #BAD PASS
    add_bad_pass = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    add_bad_pass.blend_type = "ADD"
    add_bad_pass.inputs[2].default_value = (0, 0, 0, 1)
    add_bad_pass.location = (1800, 400)
    add_bad_pass.name = add_bad_pass.label = "Add Bad"

    sub_image_diff = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    sub_image_diff.blend_type = "SUBTRACT"
    sub_image_diff.inputs[2].default_value = (0, 0, 0, 1)
    sub_image_diff.location = (200, 1200)
    sub_image_diff.name = sub_image_diff.label = "Sub Diffuse"

    sub_image_refl = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    sub_image_refl.blend_type = "SUBTRACT"
    sub_image_refl.inputs[2].default_value = (0, 0, 0, 1)
    sub_image_refl.location = (400, 1100)
    sub_image_refl.name = sub_image_refl.label = "Sub Reflection"

    sub_image_refr = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    sub_image_refr.blend_type = "SUBTRACT"
    sub_image_refr.inputs[2].default_value = (0, 0, 0, 1)
    sub_image_refr.location = (600, 1000)
    sub_image_refr.name = sub_image_refr.label = "Sub Refraction"

    sub_image_tran = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    sub_image_tran.blend_type = "SUBTRACT"
    sub_image_tran.inputs[2].default_value = (0, 0, 0, 1)
    sub_image_tran.location = (800, 900)
    sub_image_tran.name = sub_image_tran.label = "Sub Transmission"

    sub_image_sss = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    sub_image_sss.blend_type = "SUBTRACT"
    sub_image_sss.inputs[2].default_value = (0, 0, 0, 1)
    sub_image_sss.location = (1000, 800)
    sub_image_sss.name = sub_image_sss.label = "Sub SSS"

    sub_image_vol = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    sub_image_vol.blend_type = "SUBTRACT"
    sub_image_vol.inputs[2].default_value = (0, 0, 0, 1)
    sub_image_vol.location = (1200, 700)
    sub_image_vol.name = sub_image_vol.label = "Sub Volume"

    sub_image_vole = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    sub_image_vole.blend_type = "SUBTRACT"
    sub_image_vole.inputs[2].default_value = (0, 0, 0, 1)
    sub_image_vole.location = (1400, 600)
    sub_image_vole.name = sub_image_vole.label = "Sub Volume Emission"

    sub_image_emit = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    sub_image_emit.blend_type = "SUBTRACT"
    sub_image_emit.inputs[2].default_value = (0, 0, 0, 1)
    sub_image_emit.location = (1600, 500)
    sub_image_emit.name = sub_image_emit.label = "Sub Emission"


    ##ADD IT ALL TOGETHER##
    add_diff_refl = sid_tree.nodes.new(type="CompositorNodeMixRGB")
    add_diff_refl.blend_type = "ADD"
    add_diff_refl.inputs[2].default_value = (0, 0, 0, 1)
    add_diff_refl.location = (200, 800)
    add_diff_refl.name = add_diff_refl.label = "Add Reflection and Diffuse"

    if settings.use_refraction:
        add_refr = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_refr.blend_type = "ADD"
        add_refr.inputs[2].default_value = (0, 0, 0, 1)
        add_refr.location = (400, 700)
        add_refr.name = add_refr.label = "Add Refraction"
        
    if settings.use_transmission:
        add_tran = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_tran.blend_type = "ADD"
        add_tran.inputs[2].default_value = (0, 0, 0, 1)
        add_tran.location = (600, 600)
        add_tran.name = add_tran.label = "Add Transmission"

    if settings.use_sss:
        add_sss = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_sss.blend_type = "ADD"
        add_sss.inputs[2].default_value = (0, 0, 0, 1)
        add_sss.location = (800, 500)
        add_sss.name = add_sss.label = "Add SSS"

    if settings.use_volumetric:
        add_volume = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_volume.blend_type = "ADD"
        add_volume.inputs[2].default_value = (0, 0, 0, 1)
        add_volume.location = (1000, 400)
        add_volume.name = add_volume.label = "Add Volume"

        add_volume_e = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_volume_e.blend_type = "ADD"
        add_volume_e.inputs[2].default_value = (0, 0, 0, 1)
        add_volume_e.location = (1200, 300)
        add_volume_e.name = add_volume_e.label = "Add VolumeEmission"

    if settings.use_emission:
        add_emit = sid_tree.nodes.new(type="CompositorNodeMixRGB")
        add_emit.blend_type = "ADD"
        add_emit.inputs[2].default_value = (0, 0, 0, 1)
        add_emit.location = (1400, 200)
        add_emit.name = add_emit.label = "Add Emission"


    alpha_dn = create_denoiser(sid_tree, "Denoise Alpha", (2200, -100), prefilter_quality)

    final_dn = create_denoiser(sid_tree, "Final Denoise", (2000, 100), prefilter_quality)

    seperate_node = sid_tree.nodes.new(type="CompositorNodeSepRGBA")
    seperate_node.location = (2200, 100)
    combine_node = sid_tree.nodes.new(type="CompositorNodeCombRGBA")
    combine_node.location = (2400, 100)

    # Link nodes
    sid_tree.links.new(
        diffuse_denoiser_node.outputs['Denoised Image'],
        add_diff_refl.inputs[1]
        )
    sid_tree.links.new(
        reflection_denoiser_node.outputs['Denoised Image'],
        add_diff_refl.inputs[2]
        )
    prev_output = add_diff_refl.outputs[0]

    if settings.use_refraction:
        sid_tree.links.new(
            prev_output,
            add_refr.inputs[1]
            )
        sid_tree.links.new(
            refraction_denoiser_node.outputs['Denoised Image'],
            add_refr.inputs[2]
            )
        prev_output = add_refr.outputs[0]

    if settings.use_transmission:
        sid_tree.links.new(
            prev_output,
            add_tran.inputs[1]
            )
        sid_tree.links.new(
            transmission_denoiser_node.outputs['Denoised Image'],
            add_tran.inputs[2]
            )
        prev_output = add_tran.outputs[0]

    if settings.use_sss:
        sid_tree.links.new(
            prev_output,
            add_sss.inputs[1]
            )
        sid_tree.links.new(
            sss_denoiser_node.outputs['Denoised Image'],
            add_sss.inputs[2]
            )
        prev_output = add_sss.outputs[0]

    if settings.use_volumetric:
        sid_tree.links.new(
            prev_output,
            add_volume.inputs[1]
            )
        sid_tree.links.new(
            volume_denoiser_node.outputs['Denoised Image'],
            add_volume.inputs[2]
            )

        sid_tree.links.new(
            add_volume.outputs[0],
            add_volume_e.inputs[1]
            )
        sid_tree.links.new(
            volume_e_denoiser_node.outputs['Denoised Image'],
            add_volume_e.inputs[2]
            )
        prev_output = add_volume_e.outputs[0]

    if settings.use_emission:
        sid_tree.links.new(
            prev_output,
            add_emit.inputs[1]
            )
        sid_tree.links.new(
            input_node.outputs['Emission'],
            emission_dn.inputs[0]
            )
        sid_tree.links.new(
            emission_dn.outputs[0],
            add_emit.inputs[2]
            )
        prev_output = add_emit.outputs[0]

    sid_tree.links.new(
        input_node.outputs['Noisy Image'],
        sub_image_diff.inputs[1]
        )
    sid_tree.links.new(
        input_node.outputs['Diffuse'],
        sub_image_diff.inputs[2]
        )
    sid_tree.links.new(
        input_node.outputs['Reflection'],
        sub_image_refl.inputs[2]
        )
    if settings.use_refraction:
        sid_tree.links.new(
            input_node.outputs['Refraction'],
            sub_image_refr.inputs[2]
            )
    if settings.use_transmission:
        sid_tree.links.new(
            input_node.outputs['Transmission'],
            sub_image_tran.inputs[2]
            )
    if settings.use_sss:
        sid_tree.links.new(
            input_node.outputs['SSS'],
            sub_image_sss.inputs[2]
            )
    if settings.use_emission:
        sid_tree.links.new(
            input_node.outputs['Emission'],
            sub_image_emit.inputs[2]
            )
    if settings.use_volumetric:
        sid_tree.links.new(
            input_node.outputs['Volume'],
            sub_image_vol.inputs[2]
            )
        sid_tree.links.new(
            input_node.outputs['VolumeEmission'],
            sub_image_vole.inputs[2]
            )

    sid_tree.links.new(
        sub_image_diff.outputs[0],
        sub_image_refl.inputs[1]
        )
    sid_tree.links.new(
        sub_image_refl.outputs[0],
        sub_image_refr.inputs[1]
        )
    sid_tree.links.new(
        sub_image_refr.outputs[0],
        sub_image_tran.inputs[1]
        )
    sid_tree.links.new(
        sub_image_tran.outputs[0],
        sub_image_sss.inputs[1]
        )
    sid_tree.links.new(
        sub_image_sss.outputs[0],
        sub_image_vol.inputs[1]
        )
    sid_tree.links.new(
        sub_image_vol.outputs[0],
        sub_image_vole.inputs[1]
        )
    sid_tree.links.new(
        sub_image_vole.outputs[0],
        sub_image_emit.inputs[1]
        )
    sid_tree.links.new(
        sub_image_emit.outputs[0],
        add_bad_pass.inputs[1]
        )
    sid_tree.links.new(
        prev_output,
        add_bad_pass.inputs[2]
        )

    prev_output = add_bad_pass.outputs[0]

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
    sid_tree.outputs.new("NodeSocketColor", "Denoised Reflection")

    sid_tree.links.new(
        diffuse_denoiser_node.outputs['Denoised Image'],
        output_node.inputs['Denoised Diffuse']
        )
    sid_tree.links.new(
        reflection_denoiser_node.outputs['Denoised Image'],
        output_node.inputs['Denoised Reflection']
        )

    if settings.use_refraction:
        sid_tree.outputs.new("NodeSocketColor", "Denoised Refraction")
        sid_tree.links.new(
            refraction_denoiser_node.outputs['Denoised Image'],
            output_node.inputs["Denoised Refraction"]
            )
    if settings.use_transmission:
        sid_tree.outputs.new("NodeSocketColor", "Denoised Transmission")
        sid_tree.links.new(
            transmission_denoiser_node.outputs['Denoised Image'],
            output_node.inputs["Denoised Transmission"]
            )
    if settings.use_sss:
        sid_tree.outputs.new("NodeSocketColor", "Denoised SSS")
        sid_tree.links.new(
            sss_denoiser_node.outputs['Denoised Image'],
            output_node.inputs["Denoised SSS"]
            )
    if settings.use_volumetric:
        sid_tree.outputs.new("NodeSocketColor", "Denoised Volume")
        sid_tree.links.new(
            volume_denoiser_node.outputs['Denoised Image'],
            output_node.inputs["Denoised Volume"]
            )
        sid_tree.outputs.new("NodeSocketColor", "Denoised VolumeEmission")
        sid_tree.links.new(
            volume_e_denoiser_node.outputs['Denoised Image'],
            output_node.inputs["Denoised VolumeEmission"]
            )

    if settings.use_emission:
        sid_tree.outputs.new("NodeSocketColor", "Denoised Emission")
        sid_tree.links.new(
            emission_dn.outputs[0],
            output_node.inputs["Denoised Emission"]
            )

    sid_tree.outputs.new("NodeSocketColor", "Bad Pass")
    sid_tree.links.new(
        sub_image_emit.outputs['Image'],
        output_node.inputs["Bad Pass"]
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
