import bpy
from bpy.types import Node, NodeTree
from typing import Tuple

def create_denoiser(node_tree: NodeTree,name: str = None,location: Tuple[int, int] = None,prefilter_quality: str = 'ACCURATE') -> Node:

    denoiser_node = node_tree.nodes.new(type="CompositorNodeDenoise")
    if name: denoiser_node.name = denoiser_node.label = name
    if location: denoiser_node.location = location
    denoiser_node.prefilter = prefilter_quality

    return denoiser_node
