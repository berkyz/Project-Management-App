from flask import Blueprint, request, redirect, url_for, flash
from extensions import db

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route("/project/<int:project_id>/task/create", methods=["POST"])
def create_task(project_id):
    title = request.form.get("title")
    description = request.form.get("description")
    status = request.form.get("status", "Pending")
    assigned_to_raw = request.form.get("assigned_to")
    start_date = request.form.get("start_date") or None
    end_date = request.form.get("end_date") or None
    cost = request.form.get("cost", 0)
    assigned_to = int(assigned_to_raw) if assigned_to_raw else None
    
    if title:
        db.create_task(project_id, title, description, status, assigned_to, start_date, end_date, cost)
        if assigned_to:
            db.add_user_to_project(project_id, assigned_to)
        flash("Görev başarıyla eklendi!", "success")
    else:
        flash("Görev başlığı boş bırakılamaz!", "error")
    return redirect(url_for("projects.project_detail", project_id=project_id))

@tasks_bp.route("/task/<int:task_id>/update", methods=["POST"])
def update_task(task_id):
    project_id = request.form.get("project_id")
    title = request.form.get("title")
    description = request.form.get("description")
    status = request.form.get("status")
    start_date = request.form.get("start_date") or None
    end_date = request.form.get("end_date") or None
    cost = request.form.get("cost")
    assigned_to_raw = request.form.get("assigned_to")
    
    assigned_to = int(assigned_to_raw) if assigned_to_raw else None
    
    db.update_task(task_id, title, description, status, assigned_to, start_date, end_date, cost)
    if assigned_to:
        db.add_user_to_project(int(project_id), assigned_to)
    flash("Görev güncellendi!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))

@tasks_bp.route("/task/<int:task_id>/delete/<int:project_id>")
def delete_task(task_id, project_id):
    db.delete_task(task_id)
    flash("Görev silindi!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))

@tasks_bp.route("/task/<int:task_id>/tag/add", methods=["POST"])
def add_tag_to_task(task_id):
    project_id = request.form.get("project_id")
    tag_id = request.form.get("tag_id")
    if tag_id:
        db.add_tag_to_task(task_id, int(tag_id))
        flash("Etiket göreve eklendi!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))

@tasks_bp.route("/task/<int:task_id>/tag/remove/<int:tag_id>")
def remove_tag_from_task(task_id, tag_id):
    project_id = request.args.get("project_id")
    db.remove_tag_from_task(task_id, tag_id)
    flash("Etiket görevden kaldırıldı!", "success")
    if project_id:
        return redirect(url_for("projects.project_detail", project_id=project_id))
    return redirect(url_for("main.dashboard"))

@tasks_bp.route("/task/<int:task_id>/item/add", methods=["POST"])
def add_task_item(task_id):
    project_id = request.form.get("project_id")
    item_text = request.form.get("item_text")
    if item_text:
        db.create_task_item(task_id, item_text)
        flash("Alt görev eklendi!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))

@tasks_bp.route("/task/<int:task_id>/item/<int:item_id>/toggle")
def toggle_task_item(task_id, item_id):
    project_id = request.args.get("project_id")
    db.toggle_task_item(item_id)
    return redirect(url_for("projects.project_detail", project_id=project_id))

@tasks_bp.route("/task/<int:task_id>/item/<int:item_id>/delete")
def delete_task_item(task_id, item_id):
    project_id = request.args.get("project_id")
    db.delete_task_item(item_id)
    return redirect(url_for("projects.project_detail", project_id=project_id))
