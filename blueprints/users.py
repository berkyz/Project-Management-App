from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db

users_bp = Blueprint('users', __name__)

@users_bp.route("/users", methods=["GET", "POST"])
def manage_users():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        if username:
            try:
                db.create_user(username, email)
                flash(f"Kullanıcı '{username}' başarıyla oluşturuldu!", "success")
            except Exception as e:
                flash(f"Kullanıcı oluşturulamadı (Kullanıcı adı benzersiz olmalıdır)!", "error")
        else:
            flash("Kullanıcı adı alanı zorunludur!", "error")
        return redirect(url_for("users.manage_users"))
        
    users = db.get_users()
    return render_template("users.html", users=users)

@users_bp.route("/user/<int:user_id>/delete")
def delete_user(user_id):
    db.delete_user(user_id)
    flash("Kullanıcı silindi!", "success")
    return redirect(url_for("users.manage_users"))
