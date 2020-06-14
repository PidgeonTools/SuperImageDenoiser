
bl_info = {
    "name": "Super Image Denoiser (SID)",
    "author": "Kevin Lorengel",
    "version": (2, 1),
    "blender": (2, 83, 0),
    "location": "Properties > Render > Create Super Denoiser",
    "description": "SID denoises your Cycles renders near perfectly, with only one click!",
    "warning": "",
    "wiki_url": "https://discord.gg/cnFdGQP",
    "category": "Compositor",
}

# Imports
import bpy

# Classes

class SID_Create(bpy.types.Operator):

    
    bl_idname = "object.superimagedenoise"
    bl_label = "Add Super Denoiser"
    bl_description = "Enables all the necessary passes, Creates all the nodes you need, connects them all for you, to save the time you don't need to waste"

    def execute(self, context):
        

        scene = context.scene
            
        # Initialise important settings
        scene.use_nodes = True
        RenderLayer = 0
        
        bpc = bpy.context.scene
        bpc.use_nodes = True
        
        bpvl = bpc.view_layers[RenderLayer]
        

        #Clear Compositor
        ntree = scene.node_tree

        for node in ntree.nodes:
            ntree.nodes.remove(node)
            

        
        ###Enable Passes###

        #Always on
        bpy.context.view_layer.cycles.denoising_store_passes = True
    
        #Turn-off-able
        
        #SID
        SID_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SuperImageDenoiser")
        input_node = SID_tree.nodes.new("NodeGroupInput")
        input_node.location = (-200, 0)

        output_node = SID_tree.nodes.new("NodeGroupOutput")
        output_node.location = (2200, 0)
        
                
        SID_tree.inputs.new("NodeSocketVector", "Denoising Normal")
        SID_tree.inputs.new("NodeSocketColor", "Denoising Albedo")
        SID_tree.inputs.new("NodeSocketColor", "Alpha")
        
                ##DIFFUSE##
        SID_tree.inputs.new("NodeSocketColor", "DiffDir")
        SID_tree.inputs.new("NodeSocketColor", "DiffInd")
        SID_tree.inputs.new("NodeSocketColor", "DiffCol")
        bpvl.use_pass_diffuse_direct = True
        bpvl.use_pass_diffuse_indirect = True
        bpvl.use_pass_diffuse_color = True
        DifDir = SID_tree.nodes.new(type="CompositorNodeDenoise")
        DifDir.location = 0, 1400
        DifIdr = SID_tree.nodes.new(type="CompositorNodeDenoise")
        DifIdr.location = 0, 1200
        DifAdd = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        DifAdd.blend_type = "ADD"
        DifAdd.location = 200, 1400
        DifMul = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        DifMul.blend_type = "MULTIPLY"
        DifMul.location = 400, 1400
        
        #link nodes
        SID_tree.links.new(input_node.outputs['DiffInd'], DifIdr.inputs[0])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], DifIdr.inputs[1])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], DifIdr.inputs[2])
            
        SID_tree.links.new(input_node.outputs['DiffDir'], DifDir.inputs[0])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], DifDir.inputs[1])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], DifDir.inputs[2])
            
        SID_tree.links.new(DifIdr.outputs[0], DifAdd.inputs[2])
        SID_tree.links.new(DifDir.outputs[0], DifAdd.inputs[1])
            
        SID_tree.links.new(DifAdd.outputs[0], DifMul.inputs[1])
        SID_tree.links.new(input_node.outputs['DiffCol'], DifMul.inputs[2])

                ##GLOSSYNESS##
        SID_tree.inputs.new("NodeSocketColor", "GlossDir")
        SID_tree.inputs.new("NodeSocketColor", "GlossInd")
        SID_tree.inputs.new("NodeSocketColor", "GlossCol")
        bpvl.use_pass_glossy_direct = True
        bpvl.use_pass_glossy_indirect = True
        bpvl.use_pass_glossy_color = True
        GlsDir = SID_tree.nodes.new(type="CompositorNodeDenoise")
        GlsDir.location = 0, 1000
        GlsIdr = SID_tree.nodes.new(type="CompositorNodeDenoise")
        GlsIdr.location = 0, 800
        GlsAdd = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        GlsAdd.blend_type = "ADD"
        GlsAdd.location = 200, 1000
        GlsMul = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        GlsMul.blend_type = "MULTIPLY"
        GlsMul.location = 400, 1000
        
        #link nodes
        SID_tree.links.new(input_node.outputs['GlossInd'], GlsIdr.inputs[0])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], GlsIdr.inputs[1])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], GlsIdr.inputs[2])
            
        SID_tree.links.new(input_node.outputs['GlossDir'], GlsDir.inputs[0])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], GlsDir.inputs[1])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], GlsDir.inputs[2])
            
        SID_tree.links.new(GlsIdr.outputs[0], GlsAdd.inputs[2])
        SID_tree.links.new(GlsDir.outputs[0], GlsAdd.inputs[1])
            
        SID_tree.links.new(GlsAdd.outputs[0], GlsMul.inputs[1])
        SID_tree.links.new(input_node.outputs['GlossCol'], GlsMul.inputs[2])
            
            ##TRANSMISSION##
        SID_tree.inputs.new("NodeSocketColor", "TransDir")
        SID_tree.inputs.new("NodeSocketColor", "TransInd")
        SID_tree.inputs.new("NodeSocketColor", "TransCol")
        bpvl.use_pass_transmission_direct = True
        bpvl.use_pass_transmission_indirect = True
        bpvl.use_pass_transmission_color = True
        TrnDir = SID_tree.nodes.new(type="CompositorNodeDenoise")
        TrnDir.location = 0, 600
        TrnIdr = SID_tree.nodes.new(type="CompositorNodeDenoise")
        TrnIdr.location = 0, 400
        TrnAdd = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        TrnAdd.blend_type = "ADD"
        TrnAdd.location = 200, 600
        TrnMul = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        TrnMul.blend_type = "MULTIPLY"
        TrnMul.location = 400, 600

        #link nodes
        SID_tree.links.new(input_node.outputs['TransInd'], TrnIdr.inputs[0])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], TrnIdr.inputs[1])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], TrnIdr.inputs[2])
            
        SID_tree.links.new(input_node.outputs['TransDir'], TrnDir.inputs[0])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], TrnDir.inputs[1])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], TrnDir.inputs[2])
            
        SID_tree.links.new(TrnIdr.outputs[0], TrnAdd.inputs[2])
        SID_tree.links.new(TrnDir.outputs[0], TrnAdd.inputs[1])
            
        SID_tree.links.new(TrnAdd.outputs[0], TrnMul.inputs[1])
        SID_tree.links.new(input_node.outputs['TransCol'], TrnMul.inputs[2])
            
                ##VOLUMES##
        #enable passes
        SID_tree.inputs.new("NodeSocketColor", "VolumeDir")
        SID_tree.inputs.new("NodeSocketColor", "VolumeInd")
        bpy.context.view_layer.cycles.use_pass_volume_direct = True
        bpy.context.view_layer.cycles.use_pass_volume_indirect = True
    
        #create nodes
        VolDir = SID_tree.nodes.new(type="CompositorNodeDenoise")
        VolDir.location = 0, 200
        VolIdr = SID_tree.nodes.new(type="CompositorNodeDenoise")
        VolIdr.location = 0, 0
        VolAdd = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        VolAdd.blend_type = "ADD"
        VolAdd.location = 200, 200
        
        #link nodes
        SID_tree.links.new(input_node.outputs['VolumeInd'], VolIdr.inputs[0])
            
        SID_tree.links.new(input_node.outputs['VolumeDir'], VolDir.inputs[0])
            
        SID_tree.links.new(VolIdr.outputs[0], VolAdd.inputs[2])
        SID_tree.links.new(VolDir.outputs[0], VolAdd.inputs[1])
                    
                
        Add1 = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        Add1.blend_type = "ADD"
        Add1.inputs[2].default_value = (0,0,0,1)
        Add1.location = 600, 1400
    
        Add2 = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        Add2.blend_type = "ADD"
        Add2.inputs[2].default_value = (0,0,0,1)
        Add2.location = 800, 1400 
        
        Add3 = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        Add3.blend_type = "ADD"
        Add3.inputs[2].default_value = (0,0,0,1)
        Add3.location = 1000, 1400
    
        Add4 = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        Add4.blend_type = "ADD"
        Add4.inputs[2].default_value = (0,0,0,1)
        Add4.location = 1200, 1400   
        
        Add5 = SID_tree.nodes.new(type="CompositorNodeMixRGB")
        Add5.blend_type = "ADD"
        Add5.inputs[2].default_value = (0,0,0,1)
        Add5.location = 1400, 1400
        
        FinalDN = SID_tree.nodes.new(type="CompositorNodeDenoise")
        FinalDN.location = 1600, 1400  
        
        bpvl.use_pass_emit = True
        bpvl.use_pass_environment = True
        SID_tree.inputs.new("NodeSocketColor", "Emit")
        SID_tree.inputs.new("NodeSocketColor", "Env")
        
        Seperate = SID_tree.nodes.new(type="CompositorNodeSepRGBA")
        Seperate.location = 1800, 1400 
        Combine = SID_tree.nodes.new(type="CompositorNodeCombRGBA")
        Combine.location = 2000, 1400 

        ##ADD ALL TOGETHER##

        SID_tree.links.new(DifMul.outputs[0], Add1.inputs[1])
        SID_tree.links.new(GlsMul.outputs[0], Add1.inputs[2])
        SID_tree.links.new(Add1.outputs[0], Add2.inputs[1])
        SID_tree.links.new(TrnMul.outputs[0], Add2.inputs[2])
        SID_tree.links.new(Add2.outputs[0], Add3.inputs[1])
        SID_tree.links.new(input_node.outputs['Emit'], Add3.inputs[2])
        SID_tree.links.new(Add3.outputs[0], Add4.inputs[1])
        SID_tree.links.new(input_node.outputs['Env'], Add4.inputs[2])
        SID_tree.links.new(Add4.outputs[0], Add5.inputs[1])
        SID_tree.links.new(VolAdd.outputs[0], Add5.inputs[2])
        SID_tree.links.new(Add5.outputs[0], FinalDN.inputs[0])
        SID_tree.links.new(input_node.outputs['Denoising Normal'], FinalDN.inputs[1])
        SID_tree.links.new(input_node.outputs['Denoising Albedo'], FinalDN.inputs[2])
        
        SID_tree.outputs.new("NodeSocketColor", "Denoised Image")
        SID_tree.outputs.new("NodeSocketColor", "Denoised Diffuse")
        SID_tree.outputs.new("NodeSocketColor", "Denoised Glossy")
        SID_tree.outputs.new("NodeSocketColor", "Denoised Transmission")
        SID_tree.outputs.new("NodeSocketColor", "Denoised Volume")
        
        SID_tree.links.new(Combine.outputs[0], output_node.inputs["Denoised Image"])
        SID_tree.links.new(DifMul.outputs[0], output_node.inputs["Denoised Diffuse"])
        SID_tree.links.new(GlsMul.outputs[0], output_node.inputs["Denoised Glossy"])
        SID_tree.links.new(TrnMul.outputs[0], output_node.inputs["Denoised Transmission"])
        SID_tree.links.new(VolAdd.outputs[0], output_node.inputs["Denoised Volume"])                        
        SID_tree.links.new(Seperate.outputs["R"],Combine.inputs["R"])                        
        SID_tree.links.new(Seperate.outputs["G"],Combine.inputs["G"])                        
        SID_tree.links.new(Seperate.outputs["B"],Combine.inputs["B"])                        
        SID_tree.links.new(input_node.outputs["Alpha"],Combine.inputs["A"])                        
        SID_tree.links.new(FinalDN.outputs[0],Seperate.inputs[0])
        
        ViewLayerDisplace = 0
        for x in bpy.context.scene.view_layers:
            
            #Create Basic Nodes
            RenLayers_node = ntree.nodes.new(type='CompositorNodeRLayers')
            RenLayers_node.location = -100, ViewLayerDisplace
            Composite_node = ntree.nodes.new(type='CompositorNodeComposite')
            Composite_node.location = 400, ViewLayerDisplace
            
            SID_node = scene.node_tree.nodes.new("CompositorNodeGroup")
            SID_node.node_tree = SID_tree
            SID_node.location = 200, ViewLayerDisplace
            SID_node.name = "sid_node"
            
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
            
            ntree.links.new(
                RenLayers_node.outputs["VolumeDir"],
                SID_node.inputs["VolumeDir"]
                )
            
            ntree.links.new(
                RenLayers_node.outputs["VolumeInd"],
                SID_node.inputs["VolumeInd"]
                )
            
            ntree.links.new(
                RenLayers_node.outputs["Emit"],
                SID_node.inputs["Emit"]
                )
            
            ntree.links.new(
                RenLayers_node.outputs["Env"],
                SID_node.inputs["Env"]
                )
            
            ntree.links.new(
                RenLayers_node.outputs["Alpha"],
                SID_node.inputs["Alpha"]
                )
                        
            ntree.links.new(
                RenLayers_node.outputs["Denoising Albedo"],
                SID_node.inputs["Denoising Albedo"]
                )
            
            ntree.links.new(
                RenLayers_node.outputs["Denoising Normal"],
                SID_node.inputs["Denoising Normal"]
                )

            ntree.links.new(SID_node.outputs["Denoised Image"],
                Composite_node.inputs["Image"]
                )

                
            
        
        
        return {'FINISHED'}

class SID_PT_Panel(bpy.types.Panel):

    bl_label = "Create Super Denoiser"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_category = 'Pidgeon-Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        
        Headline = layout.row()
        Headline.label(text="Click to activate SID", icon='SHADERFX')
        
        if bpy.context.scene.use_nodes == True:
            Warn = layout.row()
            Warn.label(text="Compositor nodes activated!", icon='ERROR')
            Inform = layout.row()
            Inform.label(text="       Don't worry if you just added SID!", icon='NONE')

        Button = layout.row()
        Button.operator("object.superimagedenoise")

    
# Register classes
classes = (
    SID_PT_Panel,
    SID_Create,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()