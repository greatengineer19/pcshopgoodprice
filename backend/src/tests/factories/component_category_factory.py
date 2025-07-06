import factory
from src.models import ComputerComponentCategory
from . import BaseFactory

class ComponentCategoryFactory(BaseFactory):
    class Meta:
        model = ComputerComponentCategory