from src.models import ( ComputerComponent )
from datetime import datetime
from src.api.s3_dependencies import ( bucket_name, s3_client )
from typing import List

class ImageService:
    def presigned_url_generator(self, component: ComputerComponent) -> List[str]:
        images = []
        if component.images:
            presigned_url = s3_client().generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name(), 'Key': component.images[0]},
                ExpiresIn=3600
            )
            images = [presigned_url]
            
        return images