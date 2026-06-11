from flask import Blueprint, render_template
from extensions import db

reports_bp = Blueprint('reports', __name__)

@reports_bp.route("/gantt")
def gantt_chart():
    projects = db.get_projects()
    tasks = db.get_tasks()
    users = db.get_users()
    return render_template("gantt.html", tasks=tasks, projects=projects, users=users)

@reports_bp.route("/report")
def detailed_report():
    projects = db.get_projects()
    report_data = []
    
    for proj in projects:
        tasks = db.get_tasks(proj['id'])
        users = db.get_project_users(proj['id'])
        total_budget = proj.get('budget') or 0
        total_cost = sum(t.get('cost') or 0 for t in tasks)
        
        completed_tasks = sum(1 for t in tasks if t['status'] == 'Completed')
        pending_tasks = sum(1 for t in tasks if t['status'] == 'Pending')
        in_progress_tasks = sum(1 for t in tasks if t['status'] == 'In Progress')
        
        report_data.append({
            'project': proj,
            'total_tasks': len(tasks),
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'team_size': len(users),
            'total_cost': total_cost,
            'budget': total_budget,
            'remaining_budget': total_budget - total_cost
        })
        
    return render_template("report.html", report_data=report_data)

@reports_bp.route("/report/project/<int:project_id>/print")
def print_report(project_id):
    project = db.get_project(project_id)
    if not project:
        return "Proje bulunamadı", 404
        
    tasks = db.get_tasks(project_id)
    users = db.get_project_users(project_id)
    
    total_budget = project.get('budget') or 0
    total_cost = sum(t.get('cost') or 0 for t in tasks)
    
    stats = {
        'total_tasks': len(tasks),
        'completed_tasks': sum(1 for t in tasks if t['status'] == 'Completed'),
        'in_progress_tasks': sum(1 for t in tasks if t['status'] == 'In Progress'),
        'pending_tasks': sum(1 for t in tasks if t['status'] == 'Pending'),
        'team_size': len(users),
        'total_cost': total_cost,
        'budget': total_budget,
        'remaining_budget': total_budget - total_cost
    }
    
    return render_template("print_report.html", project=project, tasks=tasks, users=users, stats=stats)
