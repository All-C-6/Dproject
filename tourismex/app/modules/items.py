from ORM import Item
from flask import render_template, request, redirect, Blueprint

module = Blueprint('entity', __name__, url_prefix='/entity')


# обработка запросов по товарам
@app.route('/goods', methods=['POST', 'GET'])
def item_processing():
    if request.method == 'POST':
        if request.form.get('send') == 'Отправить':
            print("send")
            item_name = str(request.form['item_name'])
            link = str(request.form['link'])
            price = int(request.form['price'])
            material = request.form['material']
            desc = str(request.form['description'])

            item = Item(item_name=item_name, link=link, price=price, material=material, desc=desc)

            try:
                db.session.add(item)
                db.session.commit()
                return redirect('/goods')
            except:
                return "Произошла ошибка добавления предмета. Свяжитесь с администратором."

        elif request.form.get('delete') == 'Удалить':
            item = Item.query.get_or_404(request.form['item_id'])

            try:
                db.session.delete(item)
                db.session.commit()
                return redirect('/goods')
            except:
                return "Ошибка при удалении"

        elif request.form.get('edit') == 'Редактировать':
            item = Item.query.get_or_404(request.form['item_id'])
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
        items = Item.query.order_by(Item.price).all()
        return render_template("items.html", items=items)
