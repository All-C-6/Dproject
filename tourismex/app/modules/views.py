
from flask import Blueprint, request, redirect, flash, url_for, render_template
from flask_login import logout_user, login_required, current_user
from flask_csp.csp import csp_header

views_bp = Blueprint('views', __name__, url_prefix='/entity')


# маршрутизация
@views_bp.route('/')
@csp_header({
    'default-src': "'self' 'unsafe-inline' api-maps.yandex.ru yandex.ru oauth.telegram.org telegram.org",
    'script-src': "'self' 'unsafe-eval' yandex.ru oauth.telegram.org telegram.org",
    'script-src-elem': "'self' api-maps.yandex.ru oauth.telegram.org telegram.org",
    'frame-ancestors': "oauth.telegram.org telegram.org"
})
def index():
    return render_template("inx.html")


@views_bp.route('/transport')
def transport():
    return render_template("transport.html")


@views_bp.route('/climate')
def climate():
    return render_template("climate.html")


@views_bp.route('/history')
def history():
    return render_template("history.html")


@views_bp.route('/rest_places')
def rest_places():
    return render_template("rest_places.html")


@views_bp.route('/neighbours')
def neighbours():
    return render_template("neighbours.html")


@views_bp.route('/svg_map')
def svg_map():
    print("svg_map")
    return render_template("svg_map.html")


@views_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


# управление профилем
@login_required
@views_bp.route('/user_account', methods=['POST', 'GET'])
def account_edit():
    return render_template("user_account.html", user=current_user)
