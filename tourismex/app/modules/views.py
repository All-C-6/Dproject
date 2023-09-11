
from flask import Blueprint, request, redirect, flash, url_for, render_template
from flask_login import logout_user, login_required, current_user
from flask_csp.csp import csp_header

module = Blueprint('entity', __name__, url_prefix='/entity')


# получение текущей страницы пользователя (еще не реализовано)
@module.before_request
def store_current_page():
    global current_page
    current_page = request.path


# маршрутизация
@module.route('/')
@csp_header({
    'default-src': "'self' 'unsafe-inline' api-maps.yandex.ru yandex.ru oauth.telegram.org telegram.org",
    'script-src': "'self' 'unsafe-eval' yandex.ru oauth.telegram.org telegram.org",
    'script-src-elem': "'self' api-maps.yandex.ru oauth.telegram.org telegram.org",
    'frame-ancestors': "oauth.telegram.org telegram.org"
})
def index():
    return render_template("inx.html")


@module.route('/transport')
def transport():
    return render_template("transport.html")


@module.route('/climate')
def climate():
    return render_template("climate.html")


@module.route('/history')
def history():
    return render_template("history.html")


@module.route('/rest_places')
def rest_places():
    return render_template("rest_places.html")


@module.route('/neighbours')
def neighbours():
    return render_template("neighbours.html")


@module.route('/svg_map')
def svg_map():
    print("svg_map")
    return render_template("svg_map.html")


@module.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


# управление профилем
@login_required
@module.route('/user_account', methods=['POST', 'GET'])
def account_edit():
    return render_template("user_account.html", user=current_user)
