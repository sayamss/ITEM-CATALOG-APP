from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine


Base = declarative_base()


# Creating User table for storing user data
class User(Base):

    # declaring Table Name
    __tablename__ = "user"

    # creating Columns
    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=False)


# Category table
class Category(Base):

    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    Name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @property
    def serialize(self):
        # Returning data in a serialized form
        return {

             'name': self.Name,
             'id': self.id

        }


# Creating item table
class Item(Base):

    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    Name = Column(String(250), nullable=False)
    description = Column(String, nullable=False)
    picture = Column(String, nullable=False)
    time = Column(String, nullable=False)
    id_category = Column(Integer, ForeignKey("category.id"))
    category = relationship(Category, backref="items")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @property
    def serialize(self):
        # Returning data in a serialized form
        return {

             'id': self.id,
             'name': self.Name,
             'description': self.description,
             'picture': self.picture,
             'userid': self.user_id
            }


engine = create_engine("sqlite:///itemcatalog.db")
Base.metadata.create_all(engine)
