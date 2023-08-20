from . import SID_Settings
from .Cycles.SID_Create_Group_Cycles import create_cycles_group

def create_sid_group(standard_denoiser_tree, high_denoiser_tree, super_denoiser_tree, settings: SID_Settings):
    return create_cycles_group(standard_denoiser_tree,high_denoiser_tree,super_denoiser_tree,settings)
   
    
