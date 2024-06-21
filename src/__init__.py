"""
This file registers the model with the Python SDK.
"""

from viam.components.camera import Camera
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .dataReplay import dataReplay

Registry.register_resource_creator(Camera.SUBTYPE, dataReplay.MODEL, ResourceCreatorRegistration(dataReplay.new, dataReplay.validate))
