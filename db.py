import sqlite3

class Database:
    def __init__(self, db_name="projects.db"):
        """
        Database sınıfını başlatır.
        
        Parametreler:
            db_name (str): Veritabanı dosyasının adı/yolu (Varsayılan: "projects.db").
        """
        self.db_name = db_name
        self.conn = None

    def connect(self):
        """
        Veritabanına bağlantı açar. SQLite üzerinde yabancı anahtar (Foreign Key)
        desteğini etkinleştirir ve sorgu sonuçlarının sözlük (dict) biçiminde
        dönmesini sağlayacak Row Factory ayarını yapar.
        """
        self.conn = sqlite3.connect(self.db_name)
        
        # SQLite varsayılan olarak Foreign Key (ilişkili tablo kısıtlamalarını) denetlemez.
        # İlişkisel bütünlüğü korumak için bu özelliği aktif hale getiriyoruz.
        self.conn.execute("PRAGMA foreign_keys = ON;")
        
        # Sorgu sonuçlarındaki sütun isimlerine dict (sözlük) gibi erişebilmek için Row Factory atıyoruz.
        self.conn.row_factory = sqlite3.Row  
        return self.conn

    def close(self):
        """
        Eğer açık bir veritabanı bağlantısı varsa kapatır ve bağlantı nesnesini sıfırlar.
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query, params=None):
        """
        Veritabanında sorgu çalıştırmak için ortak kullanılan yardımcı fonksiyondur.
        Bağlantı açık değilse otomatik açar, sorguyu çalıştırır, işlemi onaylar (commit)
        ve sonuçları döndürür.
        
        Parametreler:
            query (str): Çalıştırılacak SQL sorgusu.
            params (tuple/list): SQL sorgusundaki (?) yer tutucularına yazılacak parametreler.
        """
        opened_here = False
        # Eğer önceden kurulmuş bir bağlantı yoksa, bu sorgu için geçici bağlantı açıyoruz.
        if not self.conn:
            self.connect()
            opened_here = True
        
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)  # Parametreli güvenli SQL çalıştırma
            else:
                cursor.execute(query)  # Parametresiz SQL çalıştırma
            self.conn.commit()  # Yapılan değişiklikleri veritabanına kalıcı olarak kaydeder.
            return cursor.fetchall()  # Sorgunun döndürdüğü tüm satırları liste olarak alır.
        finally:
            # Eğer bağlantıyı bu fonksiyon içinde açtıysak kapatırız.
            if opened_here:
                self.close()

    def init_db(self):
        """
        Veritabanı tablolarını ve aralarındaki ilişkileri ilk kez oluşturur.
        Tablolar zaten mevcutsa herhangi bir değişiklik yapmaz (IF NOT EXISTS).
        """
        # 1. Kullanıcılar Tablosu (Sistemdeki ekip üyelerini saklar)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT
            );
        """)

        # 2. Projeler Tablosu (Ana projeleri saklar)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Proje-Kullanıcı Eşleşme Tablosu (Many-to-Many / Çoktan-Çoka İlişki Köprüsü)
        # Bir projeye birden fazla üye dahil edilebilir, bir üye birden fazla projede çalışabilir.
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS project_users (
                project_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (project_id, user_id),
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # 4. Görevler Tablosu (Projelere ait alt görevleri saklar)
        # - project_id: Görevin bağlı olduğu proje (ON DELETE CASCADE ile proje silinince görev de silinir).
        # - assigned_to: Görevin atandığı kullanıcı (ON DELETE SET NULL ile kullanıcı silinirse alan boş kalır).
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Completed')),
                assigned_to INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_to) REFERENCES users (id) ON DELETE SET NULL
            );
        """)

        # 5. Etiketler Tablosu (Kategoriler ve Aciliyet durumları)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """)

        # 6. Görev-Etiket Eşleşme Tablosu (Many-to-Many)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (task_id, tag_id),
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            );
        """)

        # 7. Alt Görevler (Listeler) Tablosu
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS task_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                item_text TEXT NOT NULL,
                is_completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
            );
        """)

        # Yeni sütunları mevcut tablolara eklemeyi dene (Eğer yoksa)
        alter_queries = [
            "ALTER TABLE projects ADD COLUMN budget REAL DEFAULT 0;",
            "ALTER TABLE projects ADD COLUMN start_date DATE;",
            "ALTER TABLE projects ADD COLUMN end_date DATE;",
            "ALTER TABLE tasks ADD COLUMN start_date DATE;",
            "ALTER TABLE tasks ADD COLUMN end_date DATE;",
            "ALTER TABLE tasks ADD COLUMN cost REAL DEFAULT 0;"
        ]
        
        for q in alter_queries:
            try:
                self.execute_query(q)
            except sqlite3.OperationalError:
                pass # Sütun zaten varsa hata verir, görmezden gel

    # --- KULLANICI (USER) CRUD İŞLEMLERİ ---

    def create_user(self, username, email=None):
        """
        Sisteme yeni bir kullanıcı ekler.
        """
        query = "INSERT INTO users (username, email) VALUES (?, ?)"
        self.execute_query(query, (username, email))

    def get_users(self):
        """
        Sistemdeki tüm kullanıcıları listeler.
        """
        query = "SELECT * FROM users"
        rows = self.execute_query(query)
        return [dict(row) for row in rows]

    def get_user(self, user_id):
        """
        ID bilgisine göre tek bir kullanıcı getirir.
        """
        query = "SELECT * FROM users WHERE id = ?"
        rows = self.execute_query(query, (user_id,))
        return dict(rows[0]) if rows else None

    def delete_user(self, user_id):
        """
        Kullanıcıyı sistemden siler.
        """
        query = "DELETE FROM users WHERE id = ?"
        self.execute_query(query, (user_id,))

    # --- PROJE-KULLANICI İLİŞKİSİ İŞLEMLERİ ---

    def add_user_to_project(self, project_id, user_id):
        """
        Bir kullanıcıyı bir projeye üye olarak ekler.
        """
        query = "INSERT OR IGNORE INTO project_users (project_id, user_id) VALUES (?, ?)"
        self.execute_query(query, (project_id, user_id))

    def remove_user_from_project(self, project_id, user_id):
        """
        Bir kullanıcının proje üyeliğini kaldırır.
        """
        query = "DELETE FROM project_users WHERE project_id = ? AND user_id = ?"
        self.execute_query(query, (project_id, user_id))

    def get_project_users(self, project_id):
        """
        Belirtilen projede kayıtlı olan tüm kullanıcıları listeler.
        """
        query = """
            SELECT u.id, u.username, u.email 
            FROM users u
            JOIN project_users pu ON u.id = pu.user_id
            WHERE pu.project_id = ?
        """
        rows = self.execute_query(query, (project_id,))
        return [dict(row) for row in rows]

    # --- PROJE CRUD İŞLEMLERİ ---

    def create_project(self, name, description=None, budget=0, start_date=None, end_date=None):
        """
        Yeni bir proje oluşturur.
        """
        query = "INSERT INTO projects (name, description, budget, start_date, end_date) VALUES (?, ?, ?, ?, ?)"
        self.execute_query(query, (name, description, budget, start_date, end_date))

    def get_projects(self):
        """
        Tüm projeleri listeler.
        """
        query = "SELECT * FROM projects"
        rows = self.execute_query(query)
        return [dict(row) for row in rows]

    def get_project(self, project_id):
        """
        ID'ye göre proje getirir.
        """
        query = "SELECT * FROM projects WHERE id = ?"
        rows = self.execute_query(query, (project_id,))
        return dict(rows[0]) if rows else None

    def update_project(self, project_id, name=None, description=None, budget=None, start_date=None, end_date=None):
        """
        Proje bilgilerini günceller.
        """
        fields = []
        params = []
        if name is not None:
            fields.append("name = ?")
            params.append(name)
        if description is not None:
            fields.append("description = ?")
            params.append(description)
        if budget is not None:
            fields.append("budget = ?")
            params.append(budget)
        if start_date is not None:
            fields.append("start_date = ?")
            params.append(start_date)
        if end_date is not None:
            fields.append("end_date = ?")
            params.append(end_date)
        
        if not fields:
            return
        
        params.append(project_id)
        query = f"UPDATE projects SET {', '.join(fields)} WHERE id = ?"
        self.execute_query(query, params)

    def delete_project(self, project_id):
        """
        Projeyi siler. (Bağlı görevler cascade silinir)
        """
        query = "DELETE FROM projects WHERE id = ?"
        self.execute_query(query, (project_id,))

    # --- GÖREV (TASK) CRUD İŞLEMLERİ ---

    def create_task(self, project_id, title, description=None, status='Pending', assigned_to=None, start_date=None, end_date=None, cost=0):
        """
        Proje altına atanan kişi ile birlikte yeni görev ekler.
        """
        query = "INSERT INTO tasks (project_id, title, description, status, assigned_to, start_date, end_date, cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        self.execute_query(query, (project_id, title, description, status, assigned_to, start_date, end_date, cost))

    def get_tasks(self, project_id=None):
        """
        Görevleri listeler. Atanan kullanıcının adı da dahil edilir (LEFT JOIN).
        """
        if project_id is not None:
            query = """
                SELECT t.*, u.username as assignee_name 
                FROM tasks t
                LEFT JOIN users u ON t.assigned_to = u.id
                WHERE t.project_id = ?
            """
            rows = self.execute_query(query, (project_id,))
        else:
            query = """
                SELECT t.*, u.username as assignee_name 
                FROM tasks t
                LEFT JOIN users u ON t.assigned_to = u.id
            """
            rows = self.execute_query(query)
        return [dict(row) for row in rows]

    def get_task(self, task_id):
        """
        Görevi detaylarıyla getirir.
        """
        query = """
            SELECT t.*, u.username as assignee_name 
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.id
            WHERE t.id = ?
        """
        rows = self.execute_query(query, (task_id,))
        return dict(rows[0]) if rows else None

    def update_task(self, task_id, title=None, description=None, status=None, assigned_to=None, start_date=None, end_date=None, cost=None):
        """
        Görev bilgilerini ve atanan kişiyi günceller.
        """
        fields = []
        params = []
        if title is not None:
            fields.append("title = ?")
            params.append(title)
        if description is not None:
            fields.append("description = ?")
            params.append(description)
        if status is not None:
            fields.append("status = ?")
            params.append(status)
        if start_date is not None:
            fields.append("start_date = ?")
            params.append(start_date)
        if end_date is not None:
            fields.append("end_date = ?")
            params.append(end_date)
        if cost is not None:
            fields.append("cost = ?")
            params.append(cost)
        # assigned_to parametresini güncelleyebilmek için check (None veya tamsayı)
        fields.append("assigned_to = ?")
        params.append(assigned_to)
        
        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        self.execute_query(query, params)

    def delete_task(self, task_id):
        """
        Görevi siler.
        """
        query = "DELETE FROM tasks WHERE id = ?"
        self.execute_query(query, (task_id,))

    # --- ETİKET (TAG) CRUD İŞLEMLERİ ---

    def create_tag(self, name):
        """
        Yeni etiket oluşturur.
        """
        query = "INSERT OR IGNORE INTO tags (name) VALUES (?)"
        self.execute_query(query, (name,))

    def get_tags(self):
        """
        Tüm etiketleri listeler.
        """
        query = "SELECT * FROM tags"
        rows = self.execute_query(query)
        return [dict(row) for row in rows]

    def delete_tag(self, tag_id):
        """
        Etiketi siler.
        """
        query = "DELETE FROM tags WHERE id = ?"
        self.execute_query(query, (tag_id,))

    # --- GÖREV-ETİKET İLİŞKİSİ ---

    def add_tag_to_task(self, task_id, tag_id):
        """
        Göreve etiket atar.
        """
        query = "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)"
        self.execute_query(query, (task_id, tag_id))

    def remove_tag_from_task(self, task_id, tag_id):
        """
        Görevden etiket siler.
        """
        query = "DELETE FROM task_tags WHERE task_id = ? AND tag_id = ?"
        self.execute_query(query, (task_id, tag_id))

    def get_task_tags(self, task_id):
        """
        Görevin etiketlerini listeler.
        """
        query = """
            SELECT t.id, t.name 
            FROM tags t
            JOIN task_tags tt ON t.id = tt.tag_id
            WHERE tt.task_id = ?
        """
        rows = self.execute_query(query, (task_id,))
        return [dict(row) for row in rows]

    def get_tasks_by_tag(self, tag_id):
        """
        Belirli etiketle ilişkili görevleri getirir.
        """
        query = """
            SELECT tk.*, u.username as assignee_name 
            FROM tasks tk
            LEFT JOIN users u ON tk.assigned_to = u.id
            JOIN task_tags tt ON tk.id = tt.task_id
            WHERE tt.tag_id = ?
        """
        rows = self.execute_query(query, (tag_id,))
        return [dict(row) for row in rows]

    # --- ALT GÖREV / LİSTE İŞLEMLERİ ---

    def create_task_item(self, task_id, item_text):
        query = "INSERT INTO task_items (task_id, item_text) VALUES (?, ?)"
        self.execute_query(query, (task_id, item_text))

    def get_task_items(self, task_id):
        query = "SELECT * FROM task_items WHERE task_id = ?"
        rows = self.execute_query(query, (task_id,))
        return [dict(row) for row in rows]

    def toggle_task_item(self, item_id):
        query = "UPDATE task_items SET is_completed = NOT is_completed WHERE id = ?"
        self.execute_query(query, (item_id,))

    def delete_task_item(self, item_id):
        query = "DELETE FROM task_items WHERE id = ?"
        self.execute_query(query, (item_id,))