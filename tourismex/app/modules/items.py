from sqlalchemy import Integer, String, Float, Text

from tourismex.app.modules.classes import get_db
from flask import render_template, request, redirect, Blueprint

items_bp = Blueprint('items', __name__, url_prefix='/entity')


def get_item_model(db):
    # модель товара
    class Item(db.Model):
        item_id = db.Column(Integer, primary_key=True)
        item_name = db.Column(String(52), nullable=False)
        link = db.Column(String(100), nullable=False)
        price = db.Column(Float)
        material = db.Column(String(30))
        desc = db.Column(Text)

        def __init__(self, item_name, link, price=None, material=None, desc=None):
            self.item_name = item_name
            self.link = link
            self.price = price
            self.material = material
            self.desc = desc

        def __repr__(self):
            return f"Item('{self.item_name}', '{self.price}')"

        # Геттеры
        def get_item_id(self):
            return self.item_id

        def get_item_name(self):
            return self.item_name

        def get_link(self):
            return self.link

        def get_price(self):
            return self.price

        def get_material(self):
            return self.material

        def get_desc(self):
            return self.desc

        # Сеттеры
        def set_item_name(self, item_name):
            self.item_name = item_name

        def set_link(self, link):
            self.link = link

        def set_price(self, price):
            self.price = price

        def set_material(self, material):
            self.material = material

        def set_desc(self, desc):
            self.desc = desc

        def update_price(self, new_price):
            self.price = new_price
            db.session.commit()

        def update_material(self, new_material):
            self.material = new_material
            db.session.commit()

        def update_description(self, new_desc):
            self.desc = new_desc
            db.session.commit()

        def delete(self):
            db.session.delete(self)
            db.session.commit()

    return Item


# обработка запросов по товарам
@items_bp.route('/goods', methods=['POST', 'GET'])
def item_processing():
    db = get_db()

    item_model = get_item_model(db)
    if request.method == 'POST':

        if request.form.get('send') == 'Отправить':
            print("send")
            item_name = str(request.form['item_name'])
            link = str(request.form['link'])
            price = int(request.form['price'])
            material = request.form['material']
            desc = str(request.form['description'])

            item = item_model(item_name=item_name, link=link, price=price, material=material, desc=desc)

            try:
                db.session.add(item)
                db.session.commit()
                return redirect('/goods')
            except:
                return "Произошла ошибка добавления предмета. Свяжитесь с администратором."

        elif request.form.get('delete') == 'Удалить':
            item = item_model.query.get_or_404(request.form['item_id'])

            try:
                db.session.delete(item)
                db.session.commit()
                return redirect('/goods')
            except:
                return "Ошибка при удалении"

        elif request.form.get('edit') == 'Редактировать':
            item = item_model.query.get_or_404(request.form['item_id'])
            if request.form['item_name'] != "":
                item.item_name = str(request.form['item_name'])
            if request.form['link'] != "":
                item.link = str(request.form['link'])
            if request.form['price'] != "":
                item.link = int(request.form['price'])
            if request.form['material'] != "":
                item.material = request.form['material']
            if request.form['description'] != "":
                item.desc = str(request.form['description'])

            db.session.commit()
            return redirect('/goods')

    else:
        items = item_model.query.order_by(item_model.price).all()
        return render_template("items.html", items=items)
