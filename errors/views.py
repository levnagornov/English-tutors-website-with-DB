from flask import render_template, Blueprint


error_blp = Blueprint("error_blp", __name__)


@error_blp.errorhandler(500)
def render_server_error(error, msg="Что-то не так, но мы все починим!"):
    """Handling 500 error."""

    return render_template("error.html", msg=msg), 500


@error_blp.errorhandler(404)
def render_page_not_found(
    error, msg="Ничего не нашлось! Вот неудача, отправляйтесь на главную!"
):
    """Handling 404 error"""

    return render_template("error.html", msg=msg), 404


@error_blp.errorhandler(400)
def render_bad_request(
    error, msg="Ничего не нашлось! Вот неудача, отправляйтесь на главную!"
):
    """Handling 400 error"""

    return render_template("error.html", msg=msg), 400
