from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db

tags_bp = Blueprint('tags', __name__)

@tags_bp.route("/tags", methods=["GET", "POST"])
def manage_tags():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            db.create_tag(name)
            flash("Etiket başarıyla oluşturuldu!", "success")
        else:
            flash("Etiket adı boş olamaz!", "error")
        return redirect(url_for("tags.manage_tags"))
        
    tags = db.get_tags()
    return render_template("tags.html", tags=tags)

@tags_bp.route("/tag/<int:tag_id>/delete")
def delete_tag(tag_id):
    db.delete_tag(tag_id)
    flash("Etiket silindi!", "success")
    return redirect(url_for("tags.manage_tags"))

@tags_bp.route("/tasks/by-tag/<int:tag_id>")
def tasks_by_tag(tag_id):
    tags = db.get_tags()
    current_tag = next((t for t in tags if t['id'] == tag_id), None)
    if not current_tag:
        flash("Etiket bulunamadı!", "error")
        return redirect(url_for("main.dashboard"))
        
    tasks = db.get_tasks_by_tag(tag_id)
    tasks_with_projects = []
    for t in tasks:
        proj = db.get_project(t['project_id'])
        tasks_with_projects.append({
            'task': t,
            'project_name': proj['name'] if proj else "Bilinmeyen Proje"
        })
        
    return render_template("filtered_tasks.html", tasks=tasks_with_projects, tag=current_tag)
