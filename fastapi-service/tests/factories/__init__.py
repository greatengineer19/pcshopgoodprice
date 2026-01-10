from factory.alchemy import SQLAlchemyModelFactory

class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True