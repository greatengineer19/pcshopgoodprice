import factory
from src.models import ComputerComponentReview
from tests.factories import BaseFactory

class ComputerComponentReviewFactory(BaseFactory):
    class Meta:
        model = ComputerComponentReview

    comments = "Good product! Definitely will buy again"
    rating = 5