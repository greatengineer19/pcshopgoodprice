import factory
from src.models import ComputerComponent
from src.tests.factories import BaseFactory

class ComponentFactory(BaseFactory):
    class Meta:
        model = ComputerComponent