from typing import ClassVar, Mapping, Sequence, Any, Dict, Optional, Tuple, NamedTuple, List, cast
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
from viam.proto.app.data import BinaryID

from viam.components.camera import Camera
from viam.logging import getLogger

from PIL import Image
from io import BytesIO

LOGGER = getLogger(__name__)

class dataReplay(Camera, Reconfigurable):
    
    class Properties(NamedTuple):
        supports_pcd: bool = False
        intrinsic_parameters = None
        distortion_parameters = None
    

    MODEL: ClassVar[Model] = Model(ModelFamily("mcvella", "camera"), "data-replay")
    
    camera_properties: Camera.Properties = Properties()
    app_client : None
    api_key_id: str
    api_key: str
    dataset_name: str = ""
    dataset_id: str = ""
    binary_ids: dict
    image_index: dict

    # Constructor
    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        api_key = config.attributes.fields["app_api_key"].string_value
        if api_key == "":
            raise Exception("app_api_key attribute is required")
        api_key_id = config.attributes.fields["app_api_key_id"].string_value
        if api_key_id == "":
            raise Exception("app_api_key_id attribute is required")
        dataset_id = config.attributes.fields["default_dataset_id"].string_value
        if dataset_id == "":
            raise Exception("default_dataset_id attribute is required")
        return

    # Handles attribute reconfiguration
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.image_index = {}
        self.binary_ids = {}
        self.dataset_id = config.attributes.fields["default_dataset_id"].string_value or ""
        self.api_key = config.attributes.fields["app_api_key"].string_value
        self.api_key_id = config.attributes.fields["app_api_key_id"].string_value
        return
    
    async def viam_connect(self) -> ViamClient:
        dial_options = DialOptions.with_api_key( 
            api_key=self.api_key,
            api_key_id=self.api_key_id
        )
        return await ViamClient.create_from_dial_options(dial_options)
    
    async def get_image(
        self, mime_type: str = "", *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> ViamImage:
        if not hasattr(self, "app_client"):
            # auth to cloud for data storage
            self.app_client: ViamClient = await self.viam_connect()

        dataset_id = self.dataset_id
        if extra != None and extra.get('dataset_id') != None:
            dataset_id = extra['dataset_id']
        if not dataset_id in self.binary_ids:
            self.binary_ids[dataset_id] = []
            filter = Filter(dataset_id=dataset_id)
            done = False
            binary_args = {'filter': filter, 'include_binary_data': False}
            while not done:
                binary_ids = await self.app_client.data_client.binary_data_by_filter(**binary_args)
                if len(binary_ids[0]):
                    self.binary_ids[dataset_id].extend(binary_ids[0])
                    binary_args['last'] = binary_ids[2]
                else:
                    done = True

        if not dataset_id in self.image_index:
            self.image_index[dataset_id] = 0
        
        binary_id = BinaryID(
            file_id = self.binary_ids[dataset_id][self.image_index[dataset_id]].metadata.id,
            organization_id = self.binary_ids[dataset_id][self.image_index[dataset_id]].metadata.capture_metadata.organization_id,
            location_id = self.binary_ids[dataset_id][self.image_index[dataset_id]].metadata.capture_metadata.location_id
        )

        self.image_index[dataset_id] = self.image_index[dataset_id] + 1
        if (self.image_index[dataset_id] >= len(self.binary_ids[dataset_id])):
            self.image_index[dataset_id] = 0
        
        binary_data = await self.app_client.data_client.binary_data_by_ids(binary_ids=[binary_id])
        img = Image.open(BytesIO(binary_data[0].binary))
        return pil_to_viam_image(img.convert('RGB'), CameraMimeType.JPEG)
    
    async def get_images(self, *, timeout: Optional[float] = None, **kwargs) -> Tuple[List[NamedImage], ResponseMetadata]:
        raise NotImplementedError()


    
    async def get_point_cloud(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> Tuple[bytes, str]:
        raise NotImplementedError()

    
    async def get_properties(self, *, timeout: Optional[float] = None, **kwargs) -> Properties:
        return self.camera_properties


