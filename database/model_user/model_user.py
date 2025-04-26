from pydantic import BaseModel
from typing import Optional

class Place(BaseModel):
    user_id: str = ''
    title: str = ''
    address: str = ''
    photo_id: str = ''
    link: str = ''
    point: str = ''

    def to_dict(self):
        return {
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
            user_id = data.get('user_id'),
            title = data.get('title'),
            address = data.get('address'),
            photo_id = data.get('photo_id'),
            link = data.get('link'),
            point = data.get('point')
        )
    