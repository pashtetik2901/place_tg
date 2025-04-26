from sqlalchemy import create_engine, String, URL, select
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker
from typing import Optional
import database.model_user.model_user as model_user
from database.config_reader import config
from database.model_user.model_user import Place


class Base(DeclarativeBase):
    pass


class ModelWrite(Base):
    __tablename__ = 'places'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str]
    title: Mapped[str] = mapped_column(String(512))
    address: Mapped[Optional[str]] = mapped_column(String(512))
    photo_id: Mapped[str]
    link: Mapped[str] = mapped_column(String(1024))
    point: Mapped[Optional[str]] = mapped_column(String(1024))

    def to_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'title':self.title,
            'address':self.address,
            'photo_id':self.photo_id,
            'link': self.link,
            'point':self.point
        }
    @classmethod
    def from_dict(other, data):
        return other(
            id = data.get('id'),
            user_id = data.get('user_id'),
            title = data.get('title'),
            address = data.get('address'),
            photo_id = data.get('photo_id'),
            link = data.get('link'),
            point = data.get('point')
        )

    


data_path = config.data_url

engine = create_engine(data_path, echo=False)
Session = sessionmaker(engine)

def create_table():
    ModelWrite.metadata.create_all(engine)


def add_place_into_db(place_user: model_user.Place):
    place = ModelWrite(user_id=place_user.user_id, title=place_user.title, address=place_user.address,
                       photo_id=place_user.photo_id, link = place_user.link, point=place_user.point)
    with Session() as session:
        try:
            session.add(place)
        except:
            session.rollback()
            print('Error')
        finally:
            session.commit()

def get_place_from_db_without_point(user_id: str):
    rows = select(ModelWrite).where((ModelWrite.user_id == user_id) & (ModelWrite.point == ''))
    with Session() as session:
        try:
            data = session.scalars(rows).all()
            return data
        except:
            session.rollback()
            print('Error')

def get_place_from_db(user_id: str):
    rows = select(ModelWrite).where(ModelWrite.user_id == user_id)
    with Session() as session:
        try:
            data = session.scalars(rows).all()
            return data
        except:
            session.rollback()
            print('Error')

def get_place_for_rewrite(place_id: int):
    row = select(ModelWrite).where(ModelWrite.id == place_id)
    with Session() as session:
        try:
            data = session.scalars(row).one()
            return data
        except:
            session.rollback()
            print('Error')
    
def delete_place_from_db(place_id: int):
    row = select(ModelWrite).where(ModelWrite.id == place_id)
    with Session() as session:
        try:
            data = session.scalars(row).one()
            session.delete(data)
        except:
            session.rollback()
            print('Error')
        finally:
            session.commit()

def rewrite_place_from_db(place: ModelWrite):
    with Session() as session:
        try:
            session.merge(place)
        except:
            session.rollback()
            print('Error')
        finally:
            session.commit()



