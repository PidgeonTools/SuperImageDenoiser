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


# Classes

class SID_Settings(PropertyGroup):
    quality: EnumProperty(
        name="Quality / Compositing speed",
        items=(
            ('STANDARD', 'Standard quality / Fastest compositing', "Standard denoiser quality (fast compositing time, uses least memory)"),
            ('EXTRA', 'Better quality / Slow compositing', "Extra denoiser quality (moderate compositing time, uses a little more memory)"),
            ('HIGH', 'Highest quality / Slower compositing', "Highest denoiser quality (slower compositing time, uses significantly more memory)"),
        ),
        default='HIGH',
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


def create_sid_denoiser_high():
    # Create dual denoiser node group
    SID_denoiser_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Denoiser.HQ")
    SID_denoiser_input_node = SID_denoiser_tree.nodes.new("NodeGroupInput")
    SID_denoiser_input_node.location = (-200, 0)

    SID_denoiser_output_node = SID_denoiser_tree.nodes.new("NodeGroupOutput")
    SID_denoiser_output_node.location = (600, 0)

    SID_denoiser_tree.inputs.new("NodeSocketColor", "Direct")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Indirect")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Color")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Denoising Normal")
    SID_denoiser_tree.inputs.new("NodeSocketVector", "Denoising Albedo")
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


def create_sid_denoiser_mid():
    # Create dual denoiser node group
    SID_denoiser_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Denoiser.HQ")
    SID_denoiser_input_node = SID_denoiser_tree.nodes.new("NodeGroupInput")
    SID_denoiser_input_node.location = (-200, 0)

    SID_denoiser_output_node = SID_denoiser_tree.nodes.new("NodeGroupOutput")
    SID_denoiser_output_node.location = (600, 0)

    SID_denoiser_tree.inputs.new("NodeSocketColor", "Direct")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Indirect")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Color")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Denoising Normal")
    SID_denoiser_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
    SID_denoiser_tree.inputs['Color'].default_value = (1, 1, 1, 1)

    SID_denoiser_tree.outputs.new("NodeSocketColor", "Denoised Image")

    add_direct_indirect = SID_denoiser_tree.nodes.new(type="CompositorNodeMixRGB")
    add_direct_indirect.blend_type = "ADD"
    add_direct_indirect.location = (0, 100)
    mul_color = SID_denoiser_tree.nodes.new(type="CompositorNodeMixRGB")
    mul_color.blend_type = "MULTIPLY"
    mul_color.location = (200, 100)
    dn_node = SID_denoiser_tree.nodes.new(type="CompositorNodeDenoise")
    dn_node.location = (400, 100)

    # Link nodes
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Direct'], add_direct_indirect.inputs[1])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Indirect'], add_direct_indirect.inputs[2])

    SID_denoiser_tree.links.new(add_direct_indirect.outputs[0], mul_color.inputs[1])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Color'], mul_color.inputs[2])

    SID_denoiser_tree.links.new(mul_color.outputs[0], dn_node.inputs[0])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Normal'], dn_node.inputs[1])
    SID_denoiser_tree.links.new(SID_denoiser_input_node.outputs['Denoising Albedo'], dn_node.inputs[2])

    SID_denoiser_tree.links.new(dn_node.outputs[0], SID_denoiser_output_node.inputs['Denoised Image'])

    return SID_denoiser_tree


class SID_Create(Operator):

    bl_idname = "object.superimagedenoise"
    bl_label = "Add Super Denoiser"
    bl_description = "Enables all the necessary passes, Creates all the nodes you need, connects them all for you, to save the time you don't need to waste"

    def execute(self, context):

        scene = context.scene
        settings = scene.sid_settings

        if settings.quality == 'HIGH':
            print('Whoa, super-fancy high quality!')
        elif settings.quality == 'EXTRA':
            print('OK, a little bit extra quality, but don\'t go overboard...')
        else: # STANDARD
            print('Just standard, basic, default, boring, normal quality.')

        # Initialise important settings
        scene.render.engine = 'CYCLES'
        scene.use_nodes = True
        RenderLayer = 0


        #Clear Compositor
        ntree = scene.node_tree

        for node in ntree.nodes:
            ntree.nodes.remove(node)



        #SID
        SID_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SuperImageDenoiser")
        input_node = SID_tree.nodes.new("NodeGroupInput")
        input_node.location = (-200, 0)

        output_node = SID_tree.nodes.new("NodeGroupOutput")
        output_node.location = (1800, 0)




        SID_tree.inputs.new("NodeSocketColor", "Noisy Image")
        SID_tree.inputs.new("NodeSocketVector", "Denoising Normal")
        SID_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
        SID_tree.inputs.new("NodeSocketColor", "Alpha")



        # Create dual denoiser node group
        # TODO: if we want to create all three groups at once, remove the IF and use 2 names
        if settings.quality == 'HIGH':
            SID_denoiser_tree = create_sid_denoiser_high()
        else:
            SID_denoiser_tree = create_sid_denoiser_mid()



        # Add instances of the dual denoiser

        ##DIFFUSE##
        SID_tree.inputs.new("NodeSocketColor", "DiffDir")
        SID_tree.inputs.new("NodeSocketColor", "DiffInd")
        SID_tree.inputs.new("NodeSocketColor", "DiffCol")
        diffuse_denoiser_node = SID_tree.nodes.new("CompositorNodeGroup")
        diffuse_denoiser_node.node_tree = SID_denoiser_tree
        diffuse_denoiser_node.location = (0, 600)
        diffuse_denoiser_node.name = "Denoise Diffuse"
        diffuse_denoiser_node.label = "Denoise Diffuse"

        # link nodes
        SID_tree.links.new(input_node.outputs['DiffDir'], diffuse_denoiser_node.inputs['Direct'])
        SID_tree.links.new(input_node.outputs['DiffInd'], diffuse_denoiser_node.inputs['Indirect'])
        SID_tree.links.new(input_node.outputs['DiffCol'], diffuse_denoiser_node.inputs['Color'])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], diffuse_denoiser_node.inputs['Denoising Normal'])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], diffuse_denoiser_node.inputs['Denoising Albedo'])


        ##GLOSSY##
        SID_tree.inputs.new("NodeSocketColor", "GlossDir")
        SID_tree.inputs.new("NodeSocketColor", "GlossInd")
        SID_tree.inputs.new("NodeSocketColor", "GlossCol")
        glossy_denoiser_node = SID_tree.nodes.new("CompositorNodeGroup")
        glossy_denoiser_node.node_tree = SID_denoiser_tree
        glossy_denoiser_node.location = (0, 400)
        glossy_denoiser_node.name = "Denoise Glossy"
        glossy_denoiser_node.label = "Denoise Glossy"

        # Link nodes
        SID_tree.links.new(input_node.outputs['GlossDir'], glossy_denoiser_node.inputs['Direct'])
        SID_tree.links.new(input_node.outputs['GlossInd'], glossy_denoiser_node.inputs['Indirect'])
        SID_tree.links.new(input_node.outputs['GlossCol'], glossy_denoiser_node.inputs['Color'])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], glossy_denoiser_node.inputs['Denoising Normal'])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], glossy_denoiser_node.inputs['Denoising Albedo'])


        ##TRANSMISSION##
        SID_tree.inputs.new("NodeSocketColor", "TransDir")
        SID_tree.inputs.new("NodeSocketColor", "TransInd")
        SID_tree.inputs.new("NodeSocketColor", "TransCol")
        transmission_denoiser_node = SID_tree.nodes.new("CompositorNodeGroup")
        transmission_denoiser_node.node_tree = SID_denoiser_tree
        transmission_denoiser_node.location = (0, 200)
        transmission_denoiser_node.name = "Denoise Transmission"
        transmission_denoiser_node.label = "Denoise Transmission"

        # Link nodes
        SID_tree.links.new(input_node.outputs['TransDir'], transmission_denoiser_node.inputs['Direct'])
        SID_tree.links.new(input_node.outputs['TransInd'], transmission_denoiser_node.inputs['Indirect'])
        SID_tree.links.new(input_node.outputs['TransCol'], transmission_denoiser_node.inputs['Color'])


        ##VOLUMES##
        SID_tree.inputs.new("NodeSocketColor", "VolumeDir")
        SID_tree.inputs.new("NodeSocketColor", "VolumeInd")
        volume_denoiser_node = SID_tree.nodes.new("CompositorNodeGroup")
        volume_denoiser_node.node_tree = SID_denoiser_tree
        volume_denoiser_node.location = (0, 0)
        volume_denoiser_node.name = "Denoise Volume"
        volume_denoiser_node.label = "Denoise Volume"

        # Link nodes
        SID_tree.links.new(input_node.outputs['VolumeDir'], volume_denoiser_node.inputs['Direct'])
        SID_tree.links.new(input_node.outputs['VolumeInd'], volume_denoiser_node.inputs['Indirect'])


        # Standard Denoise
        StandardDN = SID_tree.nodes.new(type="CompositorNodeDenoise")
        StandardDN.location = 1600, -200


        ##ADD IT ALL TOGETHER##
        add_diffuse_glossy = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        add_diffuse_glossy.blend_type = "ADD"
        add_diffuse_glossy.inputs[2].default_value = (0,0,0,1)
        add_diffuse_glossy.location = (200, 500)

        add_trans = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        add_trans.blend_type = "ADD"
        add_trans.inputs[2].default_value = (0,0,0,1)
        add_trans.location = (400, 400)

        add_volume = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        add_volume.blend_type = "ADD"
        add_volume.inputs[2].default_value = (0,0,0,1)
        add_volume.location = (600, 300)

        add_emission = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        add_emission.blend_type = "ADD"
        add_emission.inputs[2].default_value = (0,0,0,1)
        add_emission.location = (800, 200)

        add_environment = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        add_environment.blend_type = "ADD"
        add_environment.inputs[2].default_value = (0,0,0,1)
        add_environment.location = (1000, 100)

        final_dn = SID_tree.nodes.new(type="CompositorNodeDenoise")
        final_dn.location = (1200, 100)

        SID_tree.inputs.new("NodeSocketColor", "Emit")
        SID_tree.inputs.new("NodeSocketColor", "Env")

        Seperate = SID_tree.nodes.new(type="CompositorNodeSepRGBA")
        Seperate.location = (1400, 100)
        Combine = SID_tree.nodes.new(type="CompositorNodeCombRGBA")
        Combine.location = (1600, 100)

        # Link nodes
        SID_tree.links.new(diffuse_denoiser_node.outputs['Denoised Image'], add_diffuse_glossy.inputs[1])
        SID_tree.links.new(glossy_denoiser_node.outputs['Denoised Image'], add_diffuse_glossy.inputs[2])
        SID_tree.links.new(add_diffuse_glossy.outputs[0], add_trans.inputs[1])
        SID_tree.links.new(transmission_denoiser_node.outputs['Denoised Image'], add_trans.inputs[2])
        SID_tree.links.new(add_trans.outputs[0], add_volume.inputs[1])
        SID_tree.links.new(volume_denoiser_node.outputs['Denoised Image'], add_volume.inputs[2])
        SID_tree.links.new(add_volume.outputs[0], add_emission.inputs[1])
        SID_tree.links.new(input_node.outputs['Emit'], add_emission.inputs[2])
        SID_tree.links.new(add_emission.outputs[0], add_environment.inputs[1])
        SID_tree.links.new(input_node.outputs['Env'], add_environment.inputs[2])
        SID_tree.links.new(add_environment.outputs[0], final_dn.inputs[0])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], final_dn.inputs[1])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], final_dn.inputs[2])
        SID_tree.links.new(input_node.outputs['Noisy Image'], StandardDN.inputs[0])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], StandardDN.inputs[1])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], StandardDN.inputs[2])

        SID_tree.outputs.new("NodeSocketColor", "Denoised Image")
        SID_tree.outputs.new("NodeSocketColor", "Denoised Diffuse")
        SID_tree.outputs.new("NodeSocketColor", "Denoised Glossy")
        SID_tree.outputs.new("NodeSocketColor", "Denoised Transmission")
        SID_tree.outputs.new("NodeSocketColor", "Denoised Volume")
        SID_tree.outputs.new("NodeSocketColor", "Standard Denoiser")

        SID_tree.links.new(Combine.outputs[0], output_node.inputs["Denoised Image"])
        SID_tree.links.new(diffuse_denoiser_node.outputs['Denoised Image'], output_node.inputs['Denoised Diffuse'])
        SID_tree.links.new(glossy_denoiser_node.outputs['Denoised Image'], output_node.inputs['Denoised Glossy'])
        SID_tree.links.new(transmission_denoiser_node.outputs['Denoised Image'], output_node.inputs["Denoised Transmission"])
        SID_tree.links.new(volume_denoiser_node.outputs['Denoised Image'], output_node.inputs["Denoised Volume"])
        SID_tree.links.new(StandardDN.outputs[0], output_node.inputs["Standard Denoiser"])
        SID_tree.links.new(Seperate.outputs["R"], Combine.inputs["R"])
        SID_tree.links.new(Seperate.outputs["G"], Combine.inputs["G"])
        SID_tree.links.new(Seperate.outputs["B"], Combine.inputs["B"])
        SID_tree.links.new(input_node.outputs["Alpha"], Combine.inputs["A"])
        SID_tree.links.new(final_dn.outputs[0], Seperate.inputs[0])


        # Create a denoiser for each View Layer
        ViewLayerDisplace = 0
        for view_layer in scene.view_layers:

            if not view_layer.use:
                continue

            #Create Basic Nodes
            RenLayers_node = ntree.nodes.new(type='CompositorNodeRLayers')
            RenLayers_node.location = (-100, ViewLayerDisplace)
            RenLayers_node.layer = view_layer.name
            Composite_node = ntree.nodes.new(type='CompositorNodeComposite')
            Composite_node.location = (400, ViewLayerDisplace)

            SID_node = scene.node_tree.nodes.new("CompositorNodeGroup")
            SID_node.node_tree = SID_tree
            SID_node.location = (200, ViewLayerDisplace)
            SID_node.name = "sid_node"


            # Prepare View Layer

            ###Enable Passes###
            view_layer.cycles.denoising_store_passes = True
            # Diffuse
            view_layer.use_pass_diffuse_direct = True
            view_layer.use_pass_diffuse_indirect = True
            view_layer.use_pass_diffuse_color = True
            # Glossy
            view_layer.use_pass_glossy_direct = True
            view_layer.use_pass_glossy_indirect = True
            view_layer.use_pass_glossy_color = True
            # Transmission
            view_layer.use_pass_transmission_direct = settings.use_transmission
            view_layer.use_pass_transmission_indirect = settings.use_transmission
            view_layer.use_pass_transmission_color = settings.use_transmission
            # Volume
            view_layer.cycles.use_pass_volume_direct = settings.use_volumetric
            view_layer.cycles.use_pass_volume_indirect = settings.use_volumetric
            # Emission & Environment
            view_layer.use_pass_emit = settings.use_emission
            view_layer.use_pass_environment = settings.use_environment


            ViewLayerDisplace -= 1000

            ntree.links.new(
                RenLayers_node.outputs["DiffDir"],
                SID_node.inputs["DiffDir"]
                )

            ntree.links.new(
                RenLayers_node.outputs["DiffInd"],
                SID_node.inputs["DiffInd"]
                )

            ntree.links.new(
                RenLayers_node.outputs["DiffCol"],
                SID_node.inputs["DiffCol"]
                )

            ntree.links.new(
                RenLayers_node.outputs["GlossDir"],
                SID_node.inputs["GlossDir"]
                )

            ntree.links.new(
                RenLayers_node.outputs["GlossInd"],
                SID_node.inputs["GlossInd"]
                )

            ntree.links.new(
                RenLayers_node.outputs["GlossCol"],
                SID_node.inputs["GlossCol"]
                )

            if settings.use_transmission:
                ntree.links.new(
                    RenLayers_node.outputs["TransDir"],
                    SID_node.inputs["TransDir"]
                    )

                ntree.links.new(
                    RenLayers_node.outputs["TransInd"],
                    SID_node.inputs["TransInd"]
                    )

                ntree.links.new(
                    RenLayers_node.outputs["TransCol"],
                    SID_node.inputs["TransCol"]
                    )

            if settings.use_volumetric:
                ntree.links.new(
                    RenLayers_node.outputs["VolumeDir"],
                    SID_node.inputs["VolumeDir"]
                    )

                ntree.links.new(
                    RenLayers_node.outputs["VolumeInd"],
                    SID_node.inputs["VolumeInd"]
                    )

            if settings.use_emission:
                ntree.links.new(
                    RenLayers_node.outputs["Emit"],
                    SID_node.inputs["Emit"]
                    )

            if settings.use_environment:
                ntree.links.new(
                    RenLayers_node.outputs["Env"],
                    SID_node.inputs["Env"]
                    )

            ntree.links.new(
                RenLayers_node.outputs["Alpha"],
                SID_node.inputs["Alpha"]
                )

            ntree.links.new(
                RenLayers_node.outputs["Noisy Image"],
                SID_node.inputs["Noisy Image"]
                )

            ntree.links.new(
                RenLayers_node.outputs["Denoising Albedo"],
                SID_node.inputs["Denoising Albedo"]
                )

            ntree.links.new(
                RenLayers_node.outputs["Denoising Normal"],
                SID_node.inputs["Denoising Normal"]
                )

            if settings.quality == 'STANDARD':
                ntree.links.new(SID_node.outputs["Standard Denoiser"],
                    Composite_node.inputs["Image"]
                    )
            else:
                ntree.links.new(SID_node.outputs["Denoised Image"],
                    Composite_node.inputs["Image"]
                    )

        return {'FINISHED'}

class SID_PT_Panel(Panel):

    bl_label = "Create Super Denoiser"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_category = 'Pidgeon-Tools'

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='SHADERFX')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.sid_settings

        if bpy.context.scene.render.engine != 'CYCLES':
            cycles_warning = layout.column(align=True)
            cycles_warning.label(text="Intel Denoiser (OIDN) render passes require Cycles.", icon='ERROR')
            cycles_warning.label(text="       The Render Engine will be switched to Cycles.")
            layout.separator()

        if bpy.context.scene.use_nodes == True:
            compositor_warn = layout.column(align=True)
            compositor_warn.label(text="Compositor nodes detected!", icon='ERROR')
            compositor_warn.label(text="       Using Super Image Denoiser will delete all compositor nodes!")
            compositor_warn.label(text="       Ignore if you just added Super Image Denoiser.")
            layout.separator()

        quality = layout.column(align=True)
        quality.prop(settings, "quality", text="Quality")
        if settings.quality == 'STANDARD':
            quality.label(text="Denoise the whole image in a single pass.", icon='INFO')
            quality.label(text="       Maximum compositing speed and least memory consumption.")
        elif settings.quality == 'EXTRA':
            quality.label(text="Denoise related render passes in groups.", icon='INFO')
            quality.label(text="       Moderate compositing speed and increased memory consumption.")
        elif settings.quality == 'HIGH':
            quality.label(text="Denoise each render pass separately.", icon='INFO')
            quality.label(text="       Slowest compositing speed and greatly increased memory consumption.")
        layout.separator()

        passes = layout.column(align=True)
        passes.label(text="Render passes:")
        passes.prop(settings, "use_emission", text="Use Emission Pass")
        passes.prop(settings, "use_environment", text="Use Environment Pass")
        passes.prop(settings, "use_transmission", text="Use Transmission Pass")
        passes.prop(settings, "use_volumetric", text="Use Volumetric Pass")
        layout.separator()

        layout.operator("object.superimagedenoise", icon='SHADERFX')





# Register classes
classes = (
    SID_Settings,
    SID_PT_Panel,
    SID_Create,
)

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.sid_settings = PointerProperty(type=SID_Settings)

def unregister():
    from bpy.utils import unregister_class

    del bpy.types.Scene.sid_settings

    for cls in reversed(classes):
        unregister_class(cls)
