from typing import ClassVar, Mapping, Sequence, Any, Dict, Optional, Tuple, Final, List, cast
from typing_extensions import Self

import sys
from typing import Any, Dict, Final, List, Optional, Tuple

from viam.media.utils.pil import viam_to_pil_image, pil_to_viam_image, CameraMimeType
from viam.app.viam_client import ViamClient
from viam.media.video import NamedImage, ViamImage
from viam.proto.common import ResponseMetadata
from viam.proto.component.camera import GetPropertiesResponse
from viam.rpc.dial import DialOptions


if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, Vector3
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.proto.app.data import Filter

from viam.components.camera import Camera
from viam.logging import getLogger

import time
import asyncio

LOGGER = getLogger(__name__)

class dataReplay(Camera, Reconfigurable):
    
    """
    Camera represents any physical hardware that can capture frames.
    """
    Properties: "TypeAlias" = GetPropertiesResponse
    

    MODEL: ClassVar[Model] = Model(ModelFamily("mcvella", "camera"), "data-replay")
    
    app_client : None
    api_key_id: str
    api_key: str
    part_id: str
    location_id: str
    org_id: str
    dataset_name: str = ""
    dataset_id: str = ""
    binary_ids: dict
    image_index = dict

    # Constructor
    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        return

    # Handles attribute reconfiguration
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        return

    """ Implement the methods the Viam RDK defines for the Camera API (rdk:component:camera) """

    
    async def get_image(
        self, mime_type: str = "", *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> ViamImage:
        if not hasattr(self, "app_client"):
            # auth to cloud for data storage
            self.app_client: ViamClient = await self.viam_connect()

        dataset_id = self.dataset_id
        if extra != None and extra.get('dataset_id') != None:
            dataset_id = extra['dataset_id']
        if not hasattr(self.binary_ids[dataset_id]):
            filter = Filter(dataset_id=dataset_id)
            self.binary_ids[dataset_id] = self.app_client.data_client.binary_data_by_filter(filter, include_binary_data=False)

        if not hasattr(self.image_index[dataset_id]):
            self.image_index[dataset_id] = 0
            
        """Get the next image from the camera as a ViamImage.
        Be sure to close the image when finished.

        NOTE: If the mime type is ``image/vnd.viam.dep`` you can use :func:`viam.media.video.ViamImage.bytes_to_depth_array`
        to convert the data to a standard representation.

        ::

            my_camera = Camera.from_robot(robot=robot, name="my_camera")

            # Assume "frame" has a mime_type of "image/vnd.viam.dep"
            frame = await my_camera.get_image(mime_type = CameraMimeType.VIAM_RAW_DEPTH)

            # Convert "frame" to a standard 2D image representation.
            # Remove the 1st 3x8 bytes and reshape the raw bytes to List[List[Int]].
            standard_frame = frame.bytes_to_depth_array()

        Args:
            mime_type (str): The desired mime type of the image. This does not guarantee output type

        Returns:
            ViamImage: The frame
        """
        ...

    
    async def get_images(self, *, timeout: Optional[float] = None, **kwargs) -> Tuple[List[NamedImage], ResponseMetadata]:
        """Get simultaneous images from different imagers, along with associated metadata.
        This should not be used for getting a time series of images from the same imager.

        ::

            my_camera = Camera.from_robot(robot=robot, name="my_camera")

            images, metadata = await my_camera.get_images()
            img0 = images[0].image
            timestamp = metadata.captured_at

        Returns:
            Tuple[List[NamedImage], ResponseMetadata]: A tuple containing two values; the first [0] a list of images returned from the
                camera system, and the second [1] the metadata associated with this response.
        """
        ...

    
    async def get_point_cloud(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> Tuple[bytes, str]:
        """
        Get the next point cloud from the camera. This will be
        returned as bytes with a mimetype describing
        the structure of the data. The consumer of this call
        should encode the bytes into the formatted suggested
        by the mimetype.

        To deserialize the returned information into a numpy array, use the Open3D library.
        ::

            import numpy as np
            import open3d as o3d

            data, _ = await camera.get_point_cloud()

            # write the point cloud into a temporary file
            with open("/tmp/pointcloud_data.pcd", "wb") as f:
                f.write(data)
            pcd = o3d.io.read_point_cloud("/tmp/pointcloud_data.pcd")
            points = np.asarray(pcd.points)

        Returns:
            Tuple[bytes, str]: A tuple containing two values; the first [0] the pointcloud data, and the second [1] the mimetype of the
                pointcloud (e.g. PCD).
        """
        ...

    
    async def get_properties(self, *, timeout: Optional[float] = None, **kwargs) -> Properties:
        """
        Get the camera intrinsic parameters and camera distortion parameters

        ::

            my_camera = Camera.from_robot(robot=robot, name="my_camera")

            properties = await my_camera.get_properties()

        Returns:
            Properties: The properties of the camera
        """
        ...

