from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(52), nullable=False)
    link = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float)
    material = db.Column(db.String(30))
    desc = db.Column(db.Text)

    def __repr__(self):
        return 'Item %r' % self.id


@app.route('/index')
@app.route('/')
def index():
    return render_template("inx.html")


@app.route('/transport')
def transport():
    return render_template("transport.html")


@app.route('/climate')
def climate():
    return render_template("climate.html")


@app.route('/history')
def history():
    return render_template("history.html")


@app.route('/items')
def db_items():
    items = Item.query.order_by(Item.name).all()
    return render_template("items.html", items=items)


@app.route('/rest_places')
def rest_places():
    return render_template("rest_places.html")


@app.route('/neighbours')
def neighbours():
    return render_template("neighbours.html")


@app.route('/svg_map')
def svg_map():
    return render_template("svg_map.html")


@app.route('/items', methods=['POST', 'GET'])
def item_processing():
    if request.method == "POST":
        if request.form.get('send') == 'Отправить':
            name = str(request.form['item_name'])
            link = str(request.form['link'])
            price = int(request.form['price'])
            material = request.form['material']
            desc = str(request.form['description'])

            item = Item(name=name, link=link, price=price, material=material, desc=desc)

            try:
                db.session.add(item)
                db.session.commit()
                return redirect('/items')
            except:
                return "Произошла ошибка добавления предмета. Свяжитесь с администратором."

        elif request.form.get('delete') == 'Удалить':
            item = Item.query.get_or_404(request.form['item_id'])

            try:
                db.session.delete(item)
                db.session.commit()
                return redirect('/items')
            except:
                return "Ошибка при удалении"

        elif request.form.get('edit') == 'Редактировать':
            item = Item.query.get_or_404(request.form['item_id'])
            if request.form['item_name'] != "":
                item.name = str(request.form['item_name'])
            if request.form['link'] != "":
                item.link = str(request.form['link'])
            if request.form['price'] != "":
                item.link = int(request.form['price'])
            if request.form['material'] != "":
                item.material = request.form['material']
            if request.form['description'] != "":
                item.desc = str(request.form['description'])

            db.session.commit()
            return redirect('/items')


    else:
        items = Item.query.order_by(Item.price).all()
        return render_template("items.html", items=items)


if __name__ == "__main__":
    app.run(debug=True)
