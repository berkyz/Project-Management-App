from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db

projects_bp = Blueprint('projects', __name__)

@projects_bp.route("/project/new", methods=["GET", "POST"])
def create_project():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        budget = request.form.get("budget", 0)
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None
        if name:
            db.create_project(name, description, budget, start_date, end_date)
            flash("Proje başarıyla oluşturuldu!", "success")
            # Son eklenen projeyi bul ve detayına yönlendir
            projects = db.get_projects()
            if projects:
                return redirect(url_for("projects.project_detail", project_id=projects[-1]['id']))
        else:
            flash("Proje adı boş bırakılamaz!", "error")
        return redirect(url_for("main.dashboard"))
    
    # GET isteği ise animasyonlu yeni proje sayfasını render et
    return render_template("new_project.html")

@projects_bp.route("/project/<int:project_id>")
def project_detail(project_id):
    project = db.get_project(project_id)
    if not project:
        flash("Proje bulunamadı!", "error")
        return redirect(url_for("main.dashboard"))
    
    tasks = db.get_tasks(project_id)
    tasks_with_tags = []
    
    for task in tasks:
        task_tags = db.get_task_tags(task['id'])
        task_items = db.get_task_items(task['id'])
        tasks_with_tags.append({
            'id': task['id'],
            'title': task['title'],
            'description': task['description'],
            'status': task['status'],
            'assigned_to': task['assigned_to'],
            'assignee_name': task['assignee_name'],
            'start_date': dict(task).get('start_date'),
            'end_date': dict(task).get('end_date'),
            'cost': dict(task).get('cost', 0),
            'created_at': task['created_at'],
            'tags': task_tags,
            'items': task_items
        })
        
    all_tags = db.get_tags()
    project_users = db.get_project_users(project_id)
    
    all_users = db.get_users()
    member_ids = {u['id'] for u in project_users}
    non_members = [u for u in all_users if u['id'] not in member_ids]
    
    # KRONOLOJİK AĞAÇ (TREE) ALGORİTMASI
    # Görevleri başlangıç tarihlerine göre sıralayıp, bitiş tarihine göre birbirinin altına hiyerarşik ekler
    scheduled_tasks = [t for t in tasks_with_tags if t['start_date']]
    scheduled_tasks.sort(key=lambda x: x['start_date'])
    
    for t in scheduled_tasks:
        t['children'] = []
        
    task_tree = []
    for i, current_task in enumerate(scheduled_tasks):
        parent_found = False
        for j in range(i-1, -1, -1):
            potential_parent = scheduled_tasks[j]
            if potential_parent.get('end_date') and potential_parent['end_date'] <= current_task['start_date']:
                potential_parent['children'].append(current_task)
                parent_found = True
                break
        
        if not parent_found:
            task_tree.append(current_task)
    
    return render_template("project.html", 
                           project=project, 
                           tasks=tasks_with_tags, 
                           all_tags=all_tags, 
                           project_users=project_users,
                           non_members=non_members,
                           all_users=all_users,
                           task_tree=task_tree)

@projects_bp.route("/project/<int:project_id>/update", methods=["POST"])
def update_project(project_id):
    name = request.form.get("name")
    description = request.form.get("description")
    budget = request.form.get("budget")
    start_date = request.form.get("start_date") or None
    end_date = request.form.get("end_date") or None
    db.update_project(project_id, name, description, budget, start_date, end_date)
    flash("Proje detayları güncellendi!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))

@projects_bp.route("/project/<int:project_id>/delete")
def delete_project(project_id):
    db.delete_project(project_id)
    flash("Proje ve ilgili tüm verileri başarıyla silindi!", "success")
    return redirect(url_for("main.dashboard"))

@projects_bp.route("/project/<int:project_id>/user/add", methods=["POST"])
def add_user_to_project(project_id):
    user_id = request.form.get("user_id")
    if user_id:
        db.add_user_to_project(project_id, int(user_id))
        flash("Kullanıcı projeye eklendi!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))

@projects_bp.route("/project/<int:project_id>/user/remove/<int:user_id>")
def remove_user_from_project(project_id, user_id):
    db.remove_user_from_project(project_id, user_id)
    flash("Kullanıcı projeden çıkarıldı!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))
