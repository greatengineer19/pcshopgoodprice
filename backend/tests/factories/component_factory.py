import factory
from src.models import ComputerComponent
from tests.factories import BaseFactory

class ComponentFactory(BaseFactory):
    class Meta:
        model = ComputerComponent