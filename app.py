from flask import Flask, render_template, request, redirect, url_for, flash
from db import Database

app = Flask(__name__)
app.secret_key = "super_secret_rgb_key"

db = Database("projects.db")

# Veritabanı tablolarını otomatik olarak ilklendir
db.init_db()

@app.route("/")
def dashboard():
    """
    Ana Kontrol Paneli (Dashboard). Tüm projeleri ve istatistiklerini listeler.
    """
    projects = db.get_projects()
    project_stats = []
    
    for proj in projects:
        tasks = db.get_tasks(proj['id'])
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t['status'] == 'Completed')
        progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        
        project_stats.append({
            'id': proj['id'],
            'name': proj['name'],
            'description': proj['description'],
            'created_at': proj['created_at'],
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress': progress
        })
    
    all_tags = db.get_tags()
    return render_template("dashboard.html", projects=project_stats, all_tags=all_tags)

@app.route("/project/create", methods=["POST"])
def create_project():
    """
    Yeni bir proje kaydı oluşturur.
    """
    name = request.form.get("name")
    description = request.form.get("description")
    if name:
        db.create_project(name, description)
        flash("Proje başarıyla oluşturuldu!", "success")
    else:
        flash("Proje adı boş bırakılamaz!", "error")
    return redirect(url_for("dashboard"))

@app.route("/project/<int:project_id>")
def project_detail(project_id):
    """
    Proje Detay Sayfası. Projeye bağlı görevleri, proje üyelerini ve etiketleri gösterir.
    """
    project = db.get_project(project_id)
    if not project:
        flash("Proje bulunamadı!", "error")
        return redirect(url_for("dashboard"))
    
    tasks = db.get_tasks(project_id)
    tasks_with_tags = []
    
    # Her bir görevin etiketlerini de alalım
    for task in tasks:
        task_tags = db.get_task_tags(task['id'])
        tasks_with_tags.append({
            'id': task['id'],
            'title': task['title'],
            'description': task['description'],
            'status': task['status'],
            'assigned_to': task['assigned_to'],
            'assignee_name': task['assignee_name'],
            'created_at': task['created_at'],
            'tags': task_tags
        })
        
    all_tags = db.get_tags()
    project_users = db.get_project_users(project_id)
    
    # Projeye üye olmayan kullanıcıları bul (projeye eklenmek üzere listelensin)
    all_users = db.get_users()
    member_ids = {u['id'] for u in project_users}
    non_members = [u for u in all_users if u['id'] not in member_ids]
    
    return render_template("project.html", 
                           project=project, 
                           tasks=tasks_with_tags, 
                           all_tags=all_tags, 
                           project_users=project_users,
                           non_members=non_members,
                           all_users=all_users)

@app.route("/project/<int:project_id>/update", methods=["POST"])
def update_project(project_id):
    """
    Projenin adını ve açıklamasını günceller.
    """
    name = request.form.get("name")
    description = request.form.get("description")
    db.update_project(project_id, name, description)
    flash("Proje detayları güncellendi!", "success")
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/project/<int:project_id>/delete")
def delete_project(project_id):
    """
    Bir projeyi ve ona bağlı tüm görevleri siler.
    """
    db.delete_project(project_id)
    flash("Proje ve ilgili tüm verileri başarıyla silindi!", "success")
    return redirect(url_for("dashboard"))

# --- KULLANICI ATAMA & YÖNETİMİ ---

@app.route("/users", methods=["GET", "POST"])
def manage_users():
    """
    Sistemdeki kullanıcıların (ekip üyeleri) listelendiği ve oluşturulduğu sayfa.
    """
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
        return redirect(url_for("manage_users"))
        
    users = db.get_users()
    return render_template("users.html", users=users)

@app.route("/user/<int:user_id>/delete")
def delete_user(user_id):
    """
    Kullanıcıyı sistemden siler.
    """
    db.delete_user(user_id)
    flash("Kullanıcı silindi!", "success")
    return redirect(url_for("manage_users"))

@app.route("/project/<int:project_id>/user/add", methods=["POST"])
def add_user_to_project(project_id):
    """
    Kullanıcıyı projeye üye olarak ekler.
    """
    user_id = request.form.get("user_id")
    if user_id:
        db.add_user_to_project(project_id, int(user_id))
        flash("Kullanıcı projeye eklendi!", "success")
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/project/<int:project_id>/user/remove/<int:user_id>")
def remove_user_from_project(project_id, user_id):
    """
    Kullanıcının projeden üyeliğini siler.
    """
    db.remove_user_from_project(project_id, user_id)
    flash("Kullanıcı projeden çıkarıldı!", "success")
    return redirect(url_for("project_detail", project_id=project_id))

# --- GÖREV ATAMA & CRUD ---

@app.route("/project/<int:project_id>/task/create", methods=["POST"])
def create_task(project_id):
    """
    Proje altına görev ekler. Göreve bir kullanıcı atanabilir.
    """
    title = request.form.get("title")
    description = request.form.get("description")
    status = request.form.get("status", "Pending")
    assigned_to_raw = request.form.get("assigned_to")
    assigned_to = int(assigned_to_raw) if assigned_to_raw else None
    
    if title:
        db.create_task(project_id, title, description, status, assigned_to)
        if assigned_to:
            db.add_user_to_project(project_id, assigned_to)
        flash("Görev başarıyla eklendi!", "success")
    else:
        flash("Görev başlığı boş bırakılamaz!", "error")
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/task/<int:task_id>/update", methods=["POST"])
def update_task(task_id):
    """
    Görev durumunu ve atanan kullanıcıyı günceller.
    """
    project_id = request.form.get("project_id")
    title = request.form.get("title")
    description = request.form.get("description")
    status = request.form.get("status")
    assigned_to_raw = request.form.get("assigned_to")
    
    # Ekranda atanan kişi değişmediyse eski atanan kişi bilgisini koru veya formdan gelen yeni değeri set et
    assigned_to = int(assigned_to_raw) if assigned_to_raw else None
    
    db.update_task(task_id, title, description, status, assigned_to)
    if assigned_to:
        db.add_user_to_project(int(project_id), assigned_to)
    flash("Görev güncellendi!", "success")
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/task/<int:task_id>/delete/<int:project_id>")
def delete_task(task_id, project_id):
    """
    Görevi siler.
    """
    db.delete_task(task_id)
    flash("Görev silindi!", "success")
    return redirect(url_for("project_detail", project_id=project_id))

# --- ETİKET YÖNETİMİ ---

@app.route("/tags", methods=["GET", "POST"])
def manage_tags():
    """
    Küresel etiket yönetimi.
    """
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            db.create_tag(name)
            flash("Etiket başarıyla oluşturuldu!", "success")
        else:
            flash("Etiket adı boş olamaz!", "error")
        return redirect(url_for("manage_tags"))
        
    tags = db.get_tags()
    return render_template("tags.html", tags=tags)

@app.route("/tag/<int:tag_id>/delete")
def delete_tag(tag_id):
    """
    Etiketi siler.
    """
    db.delete_tag(tag_id)
    flash("Etiket silindi!", "success")
    return redirect(url_for("manage_tags"))

@app.route("/task/<int:task_id>/tag/add", methods=["POST"])
def add_tag_to_task(task_id):
    """
    Etiket atar.
    """
    project_id = request.form.get("project_id")
    tag_id = request.form.get("tag_id")
    if tag_id:
        db.add_tag_to_task(task_id, int(tag_id))
        flash("Etiket göreve eklendi!", "success")
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/task/<int:task_id>/tag/remove/<int:tag_id>")
def remove_tag_from_task(task_id, tag_id):
    """
    Etiket siler.
    """
    project_id = request.args.get("project_id")
    db.remove_tag_from_task(task_id, tag_id)
    flash("Etiket görevden kaldırıldı!", "success")
    if project_id:
        return redirect(url_for("project_detail", project_id=project_id))
    return redirect(url_for("dashboard"))

@app.route("/tasks/by-tag/<int:tag_id>")
def tasks_by_tag(tag_id):
    """
    Etikete göre görev filtreleme.
    """
    tags = db.get_tags()
    current_tag = next((t for t in tags if t['id'] == tag_id), None)
    if not current_tag:
        flash("Etiket bulunamadı!", "error")
        return redirect(url_for("dashboard"))
        
    tasks = db.get_tasks_by_tag(tag_id)
    tasks_with_projects = []
    for t in tasks:
        proj = db.get_project(t['project_id'])
        tasks_with_projects.append({
            'task': t,
            'project_name': proj['name'] if proj else "Bilinmeyen Proje"
        })
        
    return render_template("filtered_tasks.html", tasks=tasks_with_projects, tag=current_tag)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
