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
    """İnternetten Dummy Data Çekme Endpoint'i"""
    try:
        response = requests.get("https://dummyjson.com/todos?limit=3")
        data = response.json()
        
        projects = db.get_projects()
        if not projects:
            db.create_project("Otomatik API Projesi", "İnternetten çekilen veriler için", 5000)
            projects = db.get_projects()
            
        first_proj_id = projects[0]['id']
        
        for item in data.get('todos', []):
            db.create_task(
                project_id=first_proj_id, 
                title=item['todo'], 
                description="API'den çekildi.", 
                status="Completed" if item['completed'] else "Pending"
            )
        flash("İnternetten 3 adet örnek veri çekildi ve projeye eklendi!", "success")
    except Exception as e:
        flash(f"Veri çekilirken hata oluştu: {str(e)}", "error")
        
    return redirect(url_for("main.dashboard"))
