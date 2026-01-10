from sqlalchemy.orm import Session
from src.sellable_products.ratings_in_component_ids_service import RatingsInComponentIdsService
from src.sellable_products.sell_price_and_ratings_finder_service import SellPriceAndRatingsFinderService
from src.api.s3_dependencies import ( bucket_name, s3_client )

class InjectedComponentIdsAndRatingPerCategoriesService:
    def __init__(
        self,
        *,
        db: Session,
        components):
        self.db = db
        self.components = components

    def call(self):
        ratings = self.ratings_hash_map()
        components_by_category_ids = self.result_components_by_category_ids(ratings=ratings)

        return components_by_category_ids
    
    def ratings_hash_map(self) -> dict:
        component_ids = [c.id for c in self.components]
        rating_service = RatingsInComponentIdsService(db=self.db, component_ids = component_ids)
        ratings = rating_service.call()

        return ratings

    def result_components_by_category_ids(self, *, ratings) -> dict:
        components_by_category_ids = {}

        for component in self.components:
            sell_price_and_ratings_service = SellPriceAndRatingsFinderService(db=self.db, ratings=ratings, component=component)
            component = sell_price_and_ratings_service.call()
            images = []
            if component.images:
                presigned_url = s3_client().generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name(), 'Key': component.images[0]},
                    ExpiresIn=3600
                )
                images = [presigned_url]
            component.images = images
            components_by_category_ids.setdefault(component.component_category_id, []).append(component)

        return components_by_category_ids