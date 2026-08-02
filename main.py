import sqlite3
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Thiết lập màu nền ứng dụng sáng nhẹ
Window.clearcolor = (0.95, 0.95, 0.95, 1)

CURRENT_USER = {"username": "", "role": "", "full_name": ""}

# ==========================================
# 1. KHỞI TẠO CƠ SỞ DỮ LIỆU SQLITE TOÀN BỘ
# ==========================================
def init_db():
    conn = sqlite3.connect('spa_enterprise.db')
    cursor = conn.cursor()
    
    # Bảng 1: Nhân viên & Phân quyền
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            base_salary REAL DEFAULT 0
        )
    ''')
    
    # Bảng 2: Khách hàng & Bệnh án
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            skin_condition TEXT,
            medical_history TEXT
        )
    ''')
    
    # Bảng 3: Lịch hẹn
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Chờ xác nhận'
        )
    ''')
    
    # Bảng 4: Bán hàng & Hóa đơn
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            items_summary TEXT,
            total_amount REAL,
            discount_voucher REAL DEFAULT 0,
            paid_amount REAL,
            debt_amount REAL,
            created_date TEXT
        )
    ''')
    
    # Bảng 5: Lịch sử Trả nợ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debt_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            payment_amount REAL,
            payment_date TEXT
        )
    ''')
    
    # Bảng 6: Kho hàng & Mỹ phẩm
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE,
            category TEXT,
            stock_qty INTEGER,
            price REAL
        )
    ''')
    
    # Bảng 7: Chấm công
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timekeeping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT,
            date TEXT,
            status TEXT
        )
    ''')
    
    # Bảng 8: Dịch vụ & Liệu trình
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price REAL,
            tour_commission REAL DEFAULT 0
        )
    ''')
    
    # Bảng 9: Voucher
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vouchers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            discount_type TEXT,
            discount_value REAL,
            expiry_date TEXT
        )
    ''')
    
    # Bảng 10: Phiếu Tour KTV
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tour_slips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ktv_name TEXT,
            service_name TEXT,
            tour_fee REAL,
            date TEXT
        )
    ''')
    
    # Bảng 11: Chi phí hàng ngày
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            amount REAL,
            date TEXT
        )
    ''')

    # Dữ liệu tài khoản mặc định
    cursor.execute("SELECT * FROM staff WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO staff (username, password, full_name, role, base_salary) VALUES ('admin', '123', 'Quản Trị Viên', 'admin', 15000000)")
        cursor.execute("INSERT INTO staff (username, password, full_name, role, base_salary) VALUES ('quanly', '123', 'Quản Lý Spa', 'quanly', 10000000)")
        cursor.execute("INSERT INTO staff (username, password, full_name, role, base_salary) VALUES ('letan', '123', 'Lễ Tân', 'letan', 7000000)")
        cursor.execute("INSERT INTO staff (username, password, full_name, role, base_salary) VALUES ('ktv1', '123', 'Kỹ Thuật Viên 1', 'ktv', 5000000)")
        
    conn.commit()
    conn.close()

init_db()


# Helper tạo nút quay lại Dashboard an toàn
def create_back_btn():
    btn = Button(text="Trở Về Dashboard", background_color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=40)
    btn.bind(on_press=lambda instance: setattr(instance.manager, 'current', 'dashboard'))
    return btn


# ==========================================
# 2. MÀN HÌNH ĐĂNG NHẬP
# ==========================================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=12, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        layout.add_widget(Label(text="HỆ THỐNG QUẢN LÝ SPA TOÀN DIỆN", font_size=18, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=40))
        
        self.username = TextInput(hint_text="Tài khoản (admin/quanly/letan/ktv1)", multiline=False, size_hint_y=None, height=40)
        self.password = TextInput(hint_text="Mật khẩu (123)", password=True, multiline=False, size_hint_y=None, height=40)
        
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        
        self.lbl_msg = Label(text="", color=(0.8, 0.1, 0.1, 1), size_hint_y=None, height=25)
        layout.add_widget(self.lbl_msg)
        
        btn_login = Button(text="ĐĂNG NHẬP", background_color=(0.1, 0.6, 0.5, 1), bold=True, size_hint_y=None, height=45)
        btn_login.bind(on_press=self.do_login)
        layout.add_widget(btn_login)
        
        self.add_widget(layout)

    def do_login(self, instance):
        global CURRENT_USER
        u = self.username.text.strip()
        p = self.password.text.strip()
        
        conn = sqlite3.connect('spa_enterprise.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, role, full_name FROM staff WHERE username=? AND password=?", (u, p))
        res = cursor.fetchone()
        conn.close()
        
        if res:
            CURRENT_USER = {"username": res[0], "role": res[1], "full_name": res[2]}
            self.manager.get_screen('dashboard').refresh_dashboard()
            self.manager.current = 'dashboard'
        else:
            self.lbl_msg.text = "Tài khoản hoặc mật khẩu không đúng!"


# ==========================================
# 3. MÀN HÌNH DASHBOARD
# ==========================================
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=8)
        self.add_widget(self.layout)

    def refresh_dashboard(self):
        self.layout.clear_widgets()
        role = CURRENT_USER.get("role", "")
        name = CURRENT_USER.get("full_name", "")
        
        role_names = {"admin": "Admin", "quanly": "Quản Lý", "letan": "Lễ Tân", "ktv": "KTV"}
        self.layout.add_widget(Label(text=f"Xin chào: {name} [{role_names.get(role, role)}]", font_size=16, bold=True, color=(0.1, 0.4, 0.4, 1), size_hint_y=None, height=30))
        
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        if role in ['admin', 'quanly', 'letan']:
            self.add_btn(grid, "1. Khách Hàng & Bệnh Án", 'customer_module')
            self.add_btn(grid, "2. Đặt Lịch Hẹn", 'appointment_module')
            self.add_btn(grid, "3. Bán Hàng & Thanh Toán", 'pos_module')
            self.add_btn(grid, "4. Công Nợ & Trả Nợ", 'debt_module')
            self.add_btn(grid, "5. Phiếu Tour KTV", 'tour_module')
            
        if role == 'ktv':
            self.add_btn(grid, "Xem Lịch Hẹn Làm Việc", 'appointment_module')
            self.add_btn(grid, "Xem Phiếu Tour Cá Nhân", 'tour_module')
            
        if role in ['admin', 'quanly']:
            self.add_btn(grid, "6. Kho Hàng & Tồn Kho", 'inventory_module')
            self.add_btn(grid, "7. Quản Lý Mỹ Phẩm", 'cosmetics_module')
            self.add_btn(grid, "8. Chấm Công Nhân Viên", 'timekeeping_module')
            self.add_btn(grid, "9. Dịch Vụ & Liệu Trình", 'service_module')
            self.add_btn(grid, "10. Voucher Giảm Giá", 'voucher_module')
            self.add_btn(grid, "11. Chi Phí Hàng Ngày", 'expense_module')

        if role == 'admin':
            self.add_btn(grid, "12. Báo Cáo Doanh Thu", 'report_module')
            self.add_btn(grid, "13. Tự Động Tính Bảng Lương", 'payroll_module')
            self.add_btn(grid, "14. Nhân Viên & Phân Quyền", 'staff_module')
            self.add_btn(grid, "15. Cài Đặt Hệ Thống", 'setting_module')

        scroll.add_widget(grid)
        self.layout.add_widget(scroll)
        
        btn_logout = Button(text="Đăng xuất", background_color=(0.7, 0.2, 0.2, 1), size_hint_y=None, height=40)
        btn_logout.bind(on_press=lambda x: setattr(self.manager, 'current', 'login_screen'))
        self.layout.add_widget(btn_logout)

    def add_btn(self, grid, text, screen_name):
        btn = Button(text=text, background_color=(0.2, 0.5, 0.6, 1), size_hint_y=None, height=45)
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', screen_name))
        grid.add_widget(btn)


# ==========================================
# MODULE 1: KHÁCH HÀNG & BỆNH ÁN
# ==========================================
class CustomerModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="QUẢN LÝ KHÁCH HÀNG & BỆNH ÁN", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_search = TextInput(hint_text="Tìm theo tên/SĐT...", multiline=False, size_hint_y=None, height=38)
        self.inp_search.bind(text=self.load_data)
        layout.add_widget(self.inp_search)
        
        self.inp_name = TextInput(hint_text="Họ và tên (*)", multiline=False, size_hint_y=None, height=38)
        self.inp_phone = TextInput(hint_text="Số điện thoại (*)", multiline=False, size_hint_y=None, height=38)
        self.inp_skin = TextInput(hint_text="Tình trạng da", multiline=False, size_hint_y=None, height=38)
        self.inp_med = TextInput(hint_text="Tiền sử bệnh án/Dị ứng", multiline=False, size_hint_y=None, height=38)
        
        for w in [self.inp_name, self.inp_phone, self.inp_skin, self.inp_med]:
            layout.add_widget(w)
            
        btn_add = Button(text="Thêm Khách Hàng", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn_add.bind(on_press=self.add_customer)
        layout.add_widget(btn_add)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self):
        self.load_data()

    def add_customer(self, instance):
        if self.inp_name.text and self.inp_phone.text:
            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO customers (name, phone, skin_condition, medical_history) VALUES (?,?,?,?)",
                          (self.inp_name.text, self.inp_phone.text, self.inp_skin.text, self.inp_med.text))
                conn.commit()
                self.inp_name.text = ""; self.inp_phone.text = ""; self.inp_skin.text = ""; self.inp_med.text = ""
            except Exception as e:
                print("Lỗi thêm khách hàng:", e)
            conn.close()
            self.load_data()

    def load_data(self, *args):
        self.grid.clear_widgets()
        q = self.inp_search.text.strip()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT id, name, phone, skin_condition, medical_history FROM customers WHERE name LIKE ? OR phone LIKE ?", (f'%{q}%', f'%{q}%'))
        for r in c.fetchall():
            lbl = Label(text=f"[b]{r[1]}[/b] - SĐT: {r[2]}\nDa: {r[3]} | Bệnh án: {r[4]}", markup=True, size_hint_y=None, height=45, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 2: QUẢN LÝ LỊCH HẸN
# ==========================================
class AppointmentModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="ĐẶT LỊCH HẸN KHÁCH HÀNG", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_name = TextInput(hint_text="Tên khách hàng", multiline=False, size_hint_y=None, height=38)
        self.inp_phone = TextInput(hint_text="SĐT", multiline=False, size_hint_y=None, height=38)
        self.inp_date = TextInput(hint_text="Ngày (YYYY-MM-DD)", text=datetime.date.today().strftime('%Y-%m-%d'), multiline=False, size_hint_y=None, height=38)
        self.inp_time = TextInput(hint_text="Giờ (VD: 14:30)", text="10:00", multiline=False, size_hint_y=None, height=38)
        
        for w in [self.inp_name, self.inp_phone, self.inp_date, self.inp_time]:
            layout.add_widget(w)
            
        btn = Button(text="Tạo Lịch Hẹn", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.add_app)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def add_app(self, instance):
        if self.inp_name.text:
            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            c.execute("INSERT INTO appointments (customer_name, phone, date, time) VALUES (?,?,?,?)",
                      (self.inp_name.text, self.inp_phone.text, self.inp_date.text, self.inp_time.text))
            conn.commit(); conn.close()
            self.load_data()

    def load_data(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT customer_name, phone, date, time, status FROM appointments ORDER BY date DESC")
        for r in c.fetchall():
            lbl = Label(text=f"{r[2]} {r[3]} - [b]{r[0]}[/b] ({r[1]}) | Trạng thái: {r[4]}", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 3: BÁN HÀNG & THANH TOÁN (POS)
# ==========================================
class POSModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="BÁN HÀNG & THANH TOÁN", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_cust = TextInput(hint_text="Tên khách hàng", multiline=False, size_hint_y=None, height=38)
        self.inp_items = TextInput(hint_text="Dịch vụ/Mỹ phẩm sử dụng", multiline=False, size_hint_y=None, height=38)
        self.inp_total = TextInput(hint_text="Tổng tiền (VNĐ)", input_filter='float', multiline=False, size_hint_y=None, height=38)
        self.inp_paid = TextInput(hint_text="Khách thanh toán (VNĐ)", input_filter='float', multiline=False, size_hint_y=None, height=38)
        
        for w in [self.inp_cust, self.inp_items, self.inp_total, self.inp_paid]:
            layout.add_widget(w)
            
        btn = Button(text="Tạo Hóa Đơn", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.checkout)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def checkout(self, instance):
        try:
            total = float(self.inp_total.text or 0)
            paid = float(self.inp_paid.text or 0)
            debt = max(0, total - paid)
            today = datetime.date.today().strftime('%Y-%m-%d')
            
            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            c.execute("INSERT INTO sales (customer_name, items_summary, total_amount, paid_amount, debt_amount, created_date) VALUES (?,?,?,?,?,?)",
                      (self.inp_cust.text, self.inp_items.text, total, paid, debt, today))
            conn.commit(); conn.close()
            self.load_data()
        except Exception as e:
            print("Lỗi thanh toán:", e)

    def load_data(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT customer_name, total_amount, paid_amount, debt_amount, created_date FROM sales ORDER BY id DESC")
        for r in c.fetchall():
            lbl = Label(text=f"{r[4]} | Khách: [b]{r[0]}[/b] | Tổng: {r[1]:,.0f}đ | Trả: {r[2]:,.0f}đ | Nợ: {r[3]:,.0f}đ", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 4: CÔNG NỢ & TRẢ NỢ
# ==========================================
class DebtModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="THEO DÕI CÔNG NỢ KHÁCH HÀNG", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_cust = TextInput(hint_text="Tên khách trả nợ", multiline=False, size_hint_y=None, height=38)
        self.inp_pay = TextInput(hint_text="Số tiền trả (VNĐ)", input_filter='float', multiline=False, size_hint_y=None, height=38)
        
        layout.add_widget(self.inp_cust)
        layout.add_widget(self.inp_pay)
        
        btn = Button(text="Ghi Nhận Trả Nợ", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.pay_debt)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def pay_debt(self, instance):
        try:
            amt = float(self.inp_pay.text or 0)
            cust_name = self.inp_cust.text.strip()
            today = datetime.date.today().strftime('%Y-%m-%d')
            
            if not cust_name or amt <= 0: return

            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            
            # Ghi nhận lịch sử trả nợ
            c.execute("INSERT INTO debt_payments (customer_name, payment_amount, payment_date) VALUES (?,?,?)",
                      (cust_name, amt, today))
            
            # Cập nhật giảm trực tiếp dư nợ trong hóa đơn gần nhất còn nợ
            c.execute("SELECT id, debt_amount FROM sales WHERE customer_name=? AND debt_amount > 0 ORDER BY id ASC", (cust_name,))
            sales_records = c.fetchall()
            
            rem_pay = amt
            for sale_id, current_debt in sales_records:
                if rem_pay <= 0: break
                deduct = min(rem_pay, current_debt)
                new_debt = current_debt - deduct
                c.execute("UPDATE sales SET debt_amount=?, paid_amount=paid_amount+? WHERE id=?", (new_debt, deduct, sale_id))
                rem_pay -= deduct

            conn.commit()
            conn.close()
            self.load_data()
        except Exception as e:
            print("Lỗi trả nợ:", e)

    def load_data(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT customer_name, SUM(debt_amount) FROM sales GROUP BY customer_name HAVING SUM(debt_amount) > 0")
        for r in c.fetchall():
            lbl = Label(text=f"Khách hàng: [b]{r[0]}[/b] - Dư nợ: [color=ff0000]{r[1]:,.0f} VNĐ[/color]", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 5: PHIẾU TOUR KTV
# ==========================================
class TourModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="PHIẾU TOUR KỸ THUẬT VIÊN", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_ktv = TextInput(hint_text="Tên KTV (VD: ktv1)", multiline=False, size_hint_y=None, height=38)
        self.inp_service = TextInput(hint_text="Dịch vụ thực hiện", multiline=False, size_hint_y=None, height=38)
        self.inp_fee = TextInput(hint_text="Tiền tour (VNĐ)", input_filter='float', multiline=False, size_hint_y=None, height=38)
        
        for w in [self.inp_ktv, self.inp_service, self.inp_fee]:
            layout.add_widget(w)
            
        btn = Button(text="Ghi Nhận Tour", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.add_tour)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def add_tour(self, instance):
        try:
            fee = float(self.inp_fee.text or 0)
            today = datetime.date.today().strftime('%Y-%m-%d')
            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            c.execute("INSERT INTO tour_slips (ktv_name, service_name, tour_fee, date) VALUES (?,?,?,?)",
                      (self.inp_ktv.text, self.inp_service.text, fee, today))
            conn.commit(); conn.close()
            self.load_data()
        except Exception as e:
            print("Lỗi ghi tour:", e)

    def load_data(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT date, ktv_name, service_name, tour_fee FROM tour_slips ORDER BY id DESC")
        for r in c.fetchall():
            lbl = Label(text=f"{r[0]} | KTV: [b]{r[1]}[/b] - Dịch vụ: {r[2]} - Hoa hồng: {r[3]:,.0f}đ", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 6 & 7: KHO HÀNG & MỸ PHẨM
# ==========================================
class InventoryModule(Screen):
    def __init__(self, is_cosmetic=False, **kwargs):
        super().__init__(**kwargs)
        self.is_cosmetic = is_cosmetic
        cat_title = "QUẢN LÝ MỸ PHẨM" if is_cosmetic else "QUẢN LÝ KHO HÀNG & VẬT TƯ"
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text=cat_title, font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_name = TextInput(hint_text="Tên sản phẩm/mỹ phẩm", multiline=False, size_hint_y=None, height=38)
        self.inp_qty = TextInput(hint_text="Số lượng tồn kho", input_filter='int', multiline=False, size_hint_y=None, height=38)
        self.inp_price = TextInput(hint_text="Đơn giá (VNĐ)", input_filter='float', multiline=False, size_hint_y=None, height=38)
        
        for w in [self.inp_name, self.inp_qty, self.inp_price]:
            layout.add_widget(w)
            
        btn = Button(text="Nhập Kho", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.add_item)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def add_item(self, instance):
        try:
            qty = int(self.inp_qty.text or 0)
            price = float(self.inp_price.text or 0)
            category = 'Mỹ phẩm' if self.is_cosmetic else 'Vật tư'
            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            c.execute("INSERT INTO inventory (item_name, category, stock_qty, price) VALUES (?,?,?,?)",
                      (self.inp_name.text, category, qty, price))
            conn.commit(); conn.close()
            self.load_data()
        except Exception as e:
            print("Lỗi nhập kho:", e)

    def load_data(self):
        self.grid.clear_widgets()
        category = 'Mỹ phẩm' if self.is_cosmetic else 'Vật tư'
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT item_name, stock_qty, price FROM inventory WHERE category=?", (category,))
        for r in c.fetchall():
            lbl = Label(text=f"Sản phẩm: [b]{r[0]}[/b] - Tồn: [color=006600]{r[1]}[/color] - Giá: {r[2]:,.0f}đ", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 8: CHẤM CÔNG NHÂN VIÊN
# ==========================================
class TimekeepingModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="CHẤM CÔNG NHÂN VIÊN HÀNG NGÀY", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_staff = TextInput(hint_text="Tên hoặc Username nhân viên", multiline=False, size_hint_y=None, height=38)
        self.inp_status = TextInput(hint_text="Trạng thái (Có mặt / Vắng / Trễ)", text="Có mặt", multiline=False, size_hint_y=None, height=38)
        
        layout.add_widget(self.inp_staff)
        layout.add_widget(self.inp_status)
        
        btn = Button(text="Điểm Danh", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.checkin)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def checkin(self, instance):
        today = datetime.date.today().strftime('%Y-%m-%d')
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("INSERT INTO timekeeping (staff_name, date, status) VALUES (?,?,?)",
                  (self.inp_staff.text, today, self.inp_status.text))
        conn.commit(); conn.close()
        self.load_data()

    def load_data(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT date, staff_name, status FROM timekeeping ORDER BY id DESC")
        for r in c.fetchall():
            lbl = Label(text=f"Ngày: {r[0]} | NV: [b]{r[1]}[/b] -> Trạng thái: {r[2]}", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 9: DỊCH VỤ & LIỆU TRÌNH
# ==========================================
class ServiceModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="DANH MỤC DỊCH VỤ & LIỆU TRÌNH", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_name = TextInput(hint_text="Tên dịch vụ/liệu trình", multiline=False, size_hint_y=None, height=38)
        self.inp_price = TextInput(hint_text="Giá dịch vụ (VNĐ)", input_filter='float', multiline=False, size_hint_y=None, height=38)
        self.inp_tour = TextInput(hint_text="Hoa hồng Tour KTV (VNĐ)", input_filter='float', multiline=False, size_hint_y=None, height=38)
        
        for w in [self.inp_name, self.inp_price, self.inp_tour]:
            layout.add_widget(w)
            
        btn = Button(text="Thêm Dịch Vụ", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.add_service)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def add_service(self, instance):
        try:
            p = float(self.inp_price.text or 0)
            t = float(self.inp_tour.text or 0)
            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            c.execute("INSERT INTO services (name, price, tour_commission) VALUES (?,?,?)",
                      (self.inp_name.text, p, t))
            conn.commit(); conn.close()
            self.load_data()
        except Exception as e:
            print("Lỗi dịch vụ:", e)

    def load_data(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT name, price, tour_commission FROM services")
        for r in c.fetchall():
            lbl = Label(text=f"Dịch vụ: [b]{r[0]}[/b] | Giá: {r[1]:,.0f}đ | Tour KTV: {r[2]:,.0f}đ", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 10: VOUCHER GIẢM GIÁ
# ==========================================
class VoucherModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="QUẢN LÝ VOUCHER GIẢM GIÁ", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_code = TextInput(hint_text="Mã Voucher (VD: SPA2026)", multiline=False, size_hint_y=None, height=38)
        self.inp_type = TextInput(hint_text="Loại giảm (VNĐ hoặc %)", text="VNĐ", multiline=False, size_hint_y=None, height=38)
        self.inp_val = TextInput(hint_text="Giá trị giảm", input_filter='float', multiline=False, size_hint_y=None, height=38)
        
        for w in [self.inp_code, self.inp_type, self.inp_val]:
            layout.add_widget(w)
            
        btn = Button(text="Tạo Voucher", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.add_v)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def add_v(self, instance):
        try:
            v = float(self.inp_val.text or 0)
            exp = (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            c.execute("INSERT INTO vouchers (code, discount_type, discount_value, expiry_date) VALUES (?,?,?,?)",
                      (self.inp_code.text.upper(), self.inp_type.text, v, exp))
            conn.commit(); conn.close()
            self.load_data()
        except Exception as e:
            print("Lỗi voucher:", e)

    def load_data(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT code, discount_type, discount_value, expiry_date FROM vouchers")
        for r in c.fetchall():
            lbl = Label(text=f"Mã: [b]{r[0]}[/b] | Giảm: {r[2]:,.0f} {r[1]} | Hạn dùng: {r[3]}", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 11: CHI PHÍ HÀNG NGÀY
# ==========================================
class ExpenseModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="QUẢN LÝ CHI PHÍ SPA HÀNG NGÀY", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_title = TextInput(hint_text="Nội dung chi (Tiền điện, nước, trà...)", multiline=False, size_hint_y=None, height=38)
        self.inp_amt = TextInput(hint_text="Số tiền chi (VNĐ)", input_filter='float', multiline=False, size_hint_y=None, height=38)
        
        layout.add_widget(self.inp_title)
        layout.add_widget(self.inp_amt)
        
        btn = Button(text="Ghi Nhận Chi Phí", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.add_exp)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def add_exp(self, instance):
        try:
            amt = float(self.inp_amt.text or 0)
            today = datetime.date.today().strftime('%Y-%m-%d')
            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            c.execute("INSERT INTO daily_expenses (title, amount, date) VALUES (?,?,?)",
                      (self.inp_title.text, amt, today))
            conn.commit(); conn.close()
            self.load_data()
        except Exception as e:
            print("Lỗi chi phí:", e)

    def load_data(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT date, title, amount FROM daily_expenses ORDER BY id DESC")
        for r in c.fetchall():
            lbl = Label(text=f"{r[0]} | [b]{r[1]}[/b]: [color=cc0000]-{r[2]:,.0f} VNĐ[/color]", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 12: BÁO CÁO DOANH THU
# ==========================================
class ReportModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.add_widget(self.layout)

    def on_enter(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="BÁO CÁO DOANH THU & THU CHI", font_size=18, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=35))
        
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        
        # Tính tổng thu
        c.execute("SELECT SUM(paid_amount) FROM sales")
        total_sales = c.fetchone()[0] or 0
        
        # Tính tổng chi
        c.execute("SELECT SUM(amount) FROM daily_expenses")
        total_exp = c.fetchone()[0] or 0
        
        profit = total_sales - total_exp
        conn.close()
        
        box = BoxLayout(orientation='vertical', spacing=10)
        box.add_widget(Label(text=f"• TỔNG THU BÁN HÀNG: [color=008800]{total_sales:,.0f} VNĐ[/color]", markup=True, color=(0,0,0,1), font_size=16))
        box.add_widget(Label(text=f"• TỔNG CHI PHÍ SPA: [color=cc0000]{total_exp:,.0f} VNĐ[/color]", markup=True, color=(0,0,0,1), font_size=16))
        box.add_widget(Label(text=f"• LỢI NHUẬN THUẦN: [b][color=0000cc]{profit:,.0f} VNĐ[/color][/b]", markup=True, color=(0,0,0,1), font_size=18))
        
        self.layout.add_widget(box)
        self.layout.add_widget(create_back_btn())


# ==========================================
# MODULE 13: BẢNG LƯƠNG NHÂN VIÊN
# ==========================================
class PayrollModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="BẢNG TÍNH LƯƠNG NHÂN VIÊN TỰ ĐỘNG", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        
        c.execute("SELECT username, full_name, base_salary FROM staff")
        staffs = c.fetchall()
        
        for s in staffs:
            username, full_name, base_sal = s
            # Cộng tiền Tour KTV
            c.execute("SELECT SUM(tour_fee) FROM tour_slips WHERE ktv_name=?", (username,))
            tour_total = c.fetchone()[0] or 0
            
            total_salary = base_sal + tour_total
            lbl = Label(
                text=f"NV: [b]{full_name}[/b] ({username})\nLương cứng: {base_sal:,.0f}đ + Tour: {tour_total:,.0f}đ = [color=006600][b]{total_salary:,.0f} VNĐ[/b][/color]",
                markup=True, size_hint_y=None, height=45, color=(0,0,0,1)
            )
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 14: NHÂN VIÊN & PHÂN QUYỀN
# ==========================================
class StaffModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)
        layout.add_widget(Label(text="QUẢN LÝ NHÂN VIÊN & PHÂN QUYỀN", font_size=16, bold=True, color=(0.1, 0.5, 0.5, 1), size_hint_y=None, height=30))
        
        self.inp_u = TextInput(hint_text="Tài khoản (Username)", multiline=False, size_hint_y=None, height=38)
        self.inp_p = TextInput(hint_text="Mật khẩu", multiline=False, size_hint_y=None, height=38)
        self.inp_name = TextInput(hint_text="Họ và tên", multiline=False, size_hint_y=None, height=38)
        self.inp_role = TextInput(hint_text="Quyền (admin / quanly / letan / ktv)", multiline=False, size_hint_y=None, height=38)
        self.inp_sal = TextInput(hint_text="Lương cơ bản (VNĐ)", input_filter='float', multiline=False, size_hint_y=None, height=38)
        
        for w in [self.inp_u, self.inp_p, self.inp_name, self.inp_role, self.inp_sal]:
            layout.add_widget(w)
            
        btn = Button(text="Thêm Nhân Viên", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=40)
        btn.bind(on_press=self.add_staff)
        layout.add_widget(btn)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def on_enter(self): self.load_data()

    def add_staff(self, instance):
        try:
            sal = float(self.inp_sal.text or 0)
            conn = sqlite3.connect('spa_enterprise.db')
            c = conn.cursor()
            c.execute("INSERT INTO staff (username, password, full_name, role, base_salary) VALUES (?,?,?,?,?)",
                      (self.inp_u.text, self.inp_p.text, self.inp_name.text, self.inp_role.text, sal))
            conn.commit(); conn.close()
            self.load_data()
        except Exception as e:
            print("Lỗi thêm NV:", e)

    def load_data(self):
        self.grid.clear_widgets()
        conn = sqlite3.connect('spa_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT username, full_name, role, base_salary FROM staff")
        for r in c.fetchall():
            lbl = Label(text=f"[b]{r[1]}[/b] (@{r[0]}) - Quyền: [color=0000cc]{r[2]}[/color] - Lương cứng: {r[3]:,.0f}đ", markup=True, size_hint_y=None, height=35, color=(0,0,0,1))
            self.grid.add_widget(lbl)
        conn.close()


# ==========================================
# MODULE 15: CÀI ĐẶT HỆ THỐNG
# ==========================================
class SettingModule(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="CÀI ĐẶT HỆ THỐNG CƠ SỞ DỮ LIỆU", font_size=18, bold=True, color=(0.1, 0.5, 0.5, 1)))
        
        lbl_info = Label(text="• Đang dùng SQLite: [b]spa_enterprise.db[/b]\n• Phiên bản App: 3.0 Enterprise", markup=True, color=(0,0,0,1))
        layout.add_widget(lbl_info)
        
        btn_reset = Button(text="Khôi Phục Dữ Liệu Mẫu", background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=45)
        btn_reset.bind(on_press=self.reset_db)
        layout.add_widget(btn_reset)
        
        layout.add_widget(create_back_btn())
        self.add_widget(layout)

    def reset_db(self, instance):
        init_db()


# ==========================================
# KHỞI CHẠY ỨNG DỤNG TOÀN DIỆN
# ==========================================
class SpaEnterpriseApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Đăng ký toàn bộ 15 Module chính thức
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(CustomerModule(name='customer_module'))
        sm.add_widget(AppointmentModule(name='appointment_module'))
        sm.add_widget(POSModule(name='pos_module'))
        sm.add_widget(DebtModule(name='debt_module'))
        sm.add_widget(TourModule(name='tour_module'))
        sm.add_widget(InventoryModule(is_cosmetic=False, name='inventory_module'))
        sm.add_widget(InventoryModule(is_cosmetic=True, name='cosmetics_module'))
        sm.add_widget(TimekeepingModule(name='timekeeping_module'))
        sm.add_widget(ServiceModule(name='service_module'))
        sm.add_widget(VoucherModule(name='voucher_module'))
        sm.add_widget(ExpenseModule(name='expense_module'))
        sm.add_widget(ReportModule(name='report_module'))
        sm.add_widget(PayrollModule(name='payroll_module'))
        sm.add_widget(StaffModule(name='staff_module'))
        sm.add_widget(SettingModule(name='setting_module'))
        
        return sm

if __name__ == '__main__':
    SpaEnterpriseApp().run()
