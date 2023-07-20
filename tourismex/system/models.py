from tourismex import db


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(52), nullable=False)
    link = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float)
    material = db.Column(db.String(30))
    desc = db.Column(db.Text)

    def __repr__(self):
        return 'Item %r' % self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(52), nullable=False)
    telegram = db.Column(db.String(24), nullable=False)
    google = db.Column(db.String(100), nullable=False)
    vk = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    about_user = db.Column(db.Text)
    place = db.Column(db.String(48))
    avatar = db.Column(db.String(48))
