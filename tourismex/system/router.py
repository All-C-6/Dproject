from flask import render_template, request, redirect, flash

from tourismex import app, db
from tourismex.system.models import Item, User


@app.route('/index')
@app.route('/')
def index():
    return render_template("inx.html")


@app.route('/start')
def start():
    return render_template("index.html")


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


@app.route('/login', methods=['POST', 'GET'])
def login():
    link = request.form.get('link')
    if link:
        user = User.query.filter_by(link=link).first()

        if user.link == request.form.get('link'):
            next_page = request.args.get('next')
            redirect(next_page)

        else:
            flash('Данный профиль не связан ни с одной учетной записью')


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    tg, google, vk = "", "", ""
    if str(request.form['link'])[8:13] == "tg.com":
        tg = str(request.form['link'])[-1:10]
    elif str(request.form['link'])[8:17] == "google.com":
        tg = str(request.form['link'])[-1:10]
    elif str(request.form['link'])[8:13] == "vk.com":
        tg = str(request.form['link'])[-1:10]
    login = str(request.form['login'])
    if type(request.form['age']) == "int":
        age = request.form['age']
    place = str(request.form['place'])
    avatar = ""
    user = User(login=login, telegram=tg, google=google, vk=vk, age=age, place=place, avatar=avatar)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    pass


@app.route('/add_message', methods=['POST', 'GET'])
def add_message():
    pass


@app.route('/delete_message', methods=['POST', 'GET'])
def delete_message():
    pass