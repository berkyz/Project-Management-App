from flask import Blueprint, render_template, flash, redirect, url_for
from extensions import db
import requests

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def dashboard():
    """Ana Kontrol Paneli (Dashboard). Tüm projeleri ve istatistiklerini listeler."""
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

@main_bp.route("/fetch-external-data")
def fetch_external_data():
    """İnternetten Dummy Data Çekme ve Tam Teşekküllü Örnek Proje Oluşturma"""
    try:
        # 1. API'den Kullanıcı ve Görevleri Çek
        users_resp = requests.get("https://dummyjson.com/users?limit=2").json()
        todos_resp = requests.get("https://dummyjson.com/todos?limit=4").json()
        
        # 2. Örnek Projeyi Oluştur
        db.create_project(
            name="API Destekli Alfa Projesi", 
            description="Tüm sistem özelliklerinin (Ağaç, Gantt, Bütçe) görülebilmesi için internetten otomatik çekilmiş örnek proje.", 
            budget=25000,
            start_date="2026-06-01",
            end_date="2026-06-30"
        )
        projects = db.get_projects()
        new_proj_id = projects[-1]['id']
        
        # 3. Kullanıcıları Sisteme Kaydet ve Projeye Ata
        created_user_ids = []
        for u in users_resp.get('users', []):
            username = f"{u['firstName']} {u['lastName']}"
            db.create_user(username=username, email=u.get('email'))
            all_u = db.get_users()
            new_u_id = all_u[-1]['id']
            created_user_ids.append(new_u_id)
            db.add_user_to_project(new_proj_id, new_u_id)
            
        # 4. Görevleri (Tasks) Oluştur, Tarih/Maliyet ve Ekip Ata
        todos = todos_resp.get('todos', [])
        # Görevlerin ağaç şemasında birbirinin altına dallanması için sıralı tarihler
        dates = [
            ("2026-06-02", "2026-06-07"),
            ("2026-06-08", "2026-06-14"),
            ("2026-06-15", "2026-06-20"),
            ("2026-06-21", "2026-06-28")
        ]
        
        for idx, item in enumerate(todos):
            assigned_user = created_user_ids[idx % len(created_user_ids)] if created_user_ids else None
            start_d, end_d = dates[idx % len(dates)]
            status = "Completed" if item['completed'] else ("In Progress" if idx % 2 == 0 else "Pending")
            
            db.create_task(
                project_id=new_proj_id,
                title=item['todo'],
                description=f"DummyJSON API'den otomatik çekildi (Kayıt ID: {item['id']})",
                status=status,
                assigned_to=assigned_user,
                start_date=start_d,
                end_date=end_d,
                cost=1500 + (idx * 500)
            )
            
            tasks = db.get_tasks(new_proj_id)
            new_task_id = tasks[-1]['id']
            
            # 5. Alt Görevler (Checklist) Ekle
            db.create_task_item(new_task_id, "Gereksinim analizi yap")
            db.create_task_item(new_task_id, "Veri doğrulama adımı")
            if idx == 0:
                db.toggle_task_item(db.get_task_items(new_task_id)[0]['id']) # İlkini tamamlandı işaretle
            
            # 6. Etiket (Tag) Oluştur ve Bağla
            tag_name = "API" if idx % 2 == 0 else "Frontend"
            # Etiket yoksa oluştur
            all_tags = db.get_tags()
            tag_exists = next((t for t in all_tags if t['name'] == tag_name), None)
            if not tag_exists:
                db.create_tag(tag_name)
                all_tags = db.get_tags()
                tag_id = all_tags[-1]['id']
            else:
                tag_id = tag_exists['id']
                
            db.add_tag_to_task(new_task_id, tag_id)
            
        flash("İnternetten tam teşekküllü (Kullanıcılar, Bütçe, Ağaç Bağlantılı, Etiketli) örnek veri çekildi!", "success")
    except Exception as e:
        flash(f"Veri çekilirken hata oluştu: {str(e)}", "error")
        
    return redirect(url_for("main.dashboard"))
