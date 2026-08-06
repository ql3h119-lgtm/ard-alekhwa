# main.py - أرض الإخوة (نسخة مبسطة بدون KivyMD)
# By Abu Jabr

import json
import os
import hashlib
from datetime import datetime, timedelta

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import NumericProperty

# تسجيل الخط العربي
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arabic.ttf")
if os.path.exists(FONT_PATH):
    LabelBase.register(name="Arabic", fn_regular=FONT_PATH)

# مكتبة تصحيح النص العربي
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RESHAPER = True
except ImportError:
    HAS_RESHAPER = False

def AR(text):
    """تحويل النص العربي للعرض الصحيح"""
    if HAS_RESHAPER and text:
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except:
            return str(text)
    return str(text)

# ============================================================
# إعدادات المشروع
# ============================================================
PROJECT = {
    "app_name": "أرض الإخوة",
    "total_area_m2": 2506,
    "total_price": 35000,
    "brothers_count": 5,
    "share_price": 7000,
    "monthly": 1000,
    "developer": "Abu Jabr",
}

BANKS = [
    "البنك العربي", "بنك فلسطين", "بنك القدس",
    "البنك الإسلامي العربي", "البنك الوطني", "بنك الأردن",
    "بنك الإسكان", "بنك القاهرة عمان", "كاش", "حوالة", "أخرى",
]

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "land_data.json")


# ============================================================
# قاعدة البيانات
# ============================================================
class DB:
    DEFAULT_NAMES = {
        1: "الأخ الأول", 2: "الأخ الثاني", 3: "الأخ الثالث",
        4: "الأخ الرابع", 5: "الأخ الخامس"
    }

    def __init__(self):
        self.data = self._load()
        self._ensure_fields()

    def _default(self):
        d = {"password": "", "brothers": {}}
        for i in range(1, 6):
            d["brothers"][str(i)] = {
                "name": self.DEFAULT_NAMES[i],
                "notes": "",
                "payments": [],
                "next_date": datetime.now().replace(day=1).strftime("%Y-%m-%d"),
            }
        return d

    def _ensure_fields(self):
        if "password" not in self.data:
            self.data["password"] = ""
        for i in range(1, 6):
            b = self.data["brothers"].get(str(i), {})
            if "notes" not in b:
                b["notes"] = ""
            if "payments" not in b:
                b["payments"] = []
        self.save()

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return self._default()

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def has_password(self):
        return bool(self.data.get("password", ""))

    def set_password(self, pwd):
        self.data["password"] = hashlib.sha256(pwd.encode()).hexdigest()
        self.save()

    def check_password(self, pwd):
        stored = self.data.get("password", "")
        if not stored:
            return True
        return hashlib.sha256(pwd.encode()).hexdigest() == stored

    def remove_password(self):
        self.data["password"] = ""
        self.save()

    def name(self, bid):
        return self.data["brothers"][str(bid)]["name"]

    def set_name(self, bid, n):
        self.data["brothers"][str(bid)]["name"] = n
        self.save()

    def notes(self, bid):
        return self.data["brothers"][str(bid)].get("notes", "")

    def set_notes(self, bid, n):
        self.data["brothers"][str(bid)]["notes"] = n
        self.save()

    def payments(self, bid):
        return self.data["brothers"][str(bid)]["payments"]

    def paid(self, bid):
        return sum(p["amount"] for p in self.payments(bid))

    def remaining(self, bid):
        return max(0, PROJECT["share_price"] - self.paid(bid))

    def total_paid(self):
        return sum(self.paid(i) for i in range(1, 6))

    def total_remaining(self):
        return max(0, PROJECT["total_price"] - self.total_paid())

    def add_payment(self, bid, amount, date, note, bank=""):
        self.data["brothers"][str(bid)]["payments"].append({
            "amount": float(amount),
            "date": date,
            "note": note,
            "bank": bank,
        })
        self.save()

    def delete_last(self, bid):
        p = self.payments(bid)
        if p:
            p.pop()
            self.save()
            return True
        return False

    def reset(self):
        self.data = self._default()
        self.save()


# ============================================================
# ويدجت مخصصة - بطاقة
# ============================================================
class Card(BoxLayout):
    def __init__(self, bg_color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ARLabel(Label):
    """Label مع دعم العربية"""
    def __init__(self, text="", **kwargs):
        kwargs.setdefault('font_name', 'Arabic')
        super().__init__(text=AR(text), **kwargs)

    def set_text(self, text):
        self.text = AR(text)


class ARButton(Button):
    """Button مع دعم العربية"""
    def __init__(self, text="", **kwargs):
        kwargs.setdefault('font_name', 'Arabic')
        super().__init__(text=AR(text), **kwargs)

    def set_text(self, text):
        self.text = AR(text)


# ============================================================
# الشاشات
# ============================================================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        layout.add_widget(Label(size_hint_y=0.15))
        
        title = ARLabel(text="أرض الإخوة", font_size='28sp', bold=True,
                        color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=dp(50))
        layout.add_widget(title)
        
        sub = ARLabel(text="إدارة شراء الأرض المشتركة", font_size='14sp',
                      color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(sub)
        
        area = ARLabel(text=f"المساحة: {PROJECT['total_area_m2']} م²",
                       font_size='12sp', color=(0.6, 0.6, 0.6, 1),
                       size_hint_y=None, height=dp(25))
        layout.add_widget(area)
        
        layout.add_widget(Label(size_hint_y=0.1))
        
        self.pwd = TextInput(password=True, multiline=False, font_size='16sp',
                             size_hint=(0.8, None), height=dp(48),
                             pos_hint={'center_x': 0.5}, hint_text="Password")
        layout.add_widget(self.pwd)
        
        btn = ARButton(text="دخول", size_hint=(0.8, None), height=dp(48),
                       pos_hint={'center_x': 0.5},
                       background_color=(0.15, 0.15, 0.15, 1), color=(1, 1, 1, 1))
        btn.bind(on_release=self.try_login)
        layout.add_widget(btn)
        
        self.err = ARLabel(text="", color=(0.78, 0.18, 0.18, 1),
                           size_hint_y=None, height=dp(30))
        layout.add_widget(self.err)
        
        layout.add_widget(Label())
        
        dev = ARLabel(text=f"بواسطة {PROJECT['developer']}", font_size='11sp',
                      color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(25))
        layout.add_widget(dev)
        
        self.add_widget(layout)

    def on_enter(self):
        app = App.get_running_app()
        if not app.db.has_password():
            self.manager.current = "home"

    def try_login(self, *a):
        app = App.get_running_app()
        pwd = self.pwd.text.strip()
        if not app.db.has_password() or app.db.check_password(pwd):
            self.pwd.text = ""
            self.err.set_text("")
            self.manager.current = "home"
        else:
            self.err.set_text("كلمة السر خاطئة")


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=dp(10))
        with header.canvas.before:
            Color(1, 1, 1, 1)
            self.hrect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(self.hrect, 'pos', v),
                    size=lambda i, v: setattr(self.hrect, 'size', v))
        title = ARLabel(text="أرض الإخوة", font_size='22sp', bold=True,
                        color=(0.1, 0.1, 0.1, 1))
        header.add_widget(title)
        root.add_widget(header)
        
        # Scroll content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10),
                            size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Project info card
        info = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180),
                        padding=dp(14), spacing=dp(4))
        with info.canvas.before:
            Color(1, 1, 1, 1)
            self.irect = RoundedRectangle(pos=info.pos, size=info.size, radius=[dp(10)])
        info.bind(pos=lambda i, v: setattr(self.irect, 'pos', v),
                  size=lambda i, v: setattr(self.irect, 'size', v))
        
        info.add_widget(ARLabel(text="معلومات المشروع", bold=True,
                                color=(0.1, 0.1, 0.1, 1), font_size='16sp',
                                size_hint_y=None, height=dp(28), halign='right'))
        info.add_widget(ARLabel(text=f"المساحة: {PROJECT['total_area_m2']} م²",
                                color=(0.4, 0.4, 0.4, 1), font_size='13sp',
                                size_hint_y=None, height=dp(22), halign='right'))
        info.add_widget(ARLabel(text=f"السعر الكلي: {PROJECT['total_price']:,} دينار",
                                color=(0.4, 0.4, 0.4, 1), font_size='13sp',
                                size_hint_y=None, height=dp(22), halign='right'))
        info.add_widget(ARLabel(text=f"حصة كل أخ: {PROJECT['share_price']:,} دينار",
                                color=(0.4, 0.4, 0.4, 1), font_size='13sp',
                                size_hint_y=None, height=dp(22), halign='right'))
        
        self.tp_lbl = ARLabel(text="إجمالي المدفوع: 0", bold=True,
                              color=(0.12, 0.52, 0.3, 1), font_size='14sp',
                              size_hint_y=None, height=dp(24), halign='right')
        info.add_widget(self.tp_lbl)
        
        self.tr_lbl = ARLabel(text="إجمالي المتبقي: 35,000", bold=True,
                              color=(0.78, 0.18, 0.18, 1), font_size='14sp',
                              size_hint_y=None, height=dp(24), halign='right')
        info.add_widget(self.tr_lbl)
        
        content.add_widget(info)
        
        # Brothers section title
        content.add_widget(ARLabel(text="الأقساط حسب كل أخ", bold=True,
                                    color=(0.3, 0.3, 0.3, 1), font_size='14sp',
                                    size_hint_y=None, height=dp(28), halign='right'))
        
        # Brother rows
        self.brother_labels = {}
        for i in range(1, 6):
            row = self.make_brother_row(i)
            content.add_widget(row)
        
        # Buttons
        btns_box = BoxLayout(orientation='vertical', size_hint_y=None,
                            height=dp(160), padding=dp(12), spacing=dp(8))
        with btns_box.canvas.before:
            Color(1, 1, 1, 1)
            self.brect = RoundedRectangle(pos=btns_box.pos, size=btns_box.size, radius=[dp(10)])
        btns_box.bind(pos=lambda i, v: setattr(self.brect, 'pos', v),
                      size=lambda i, v: setattr(self.brect, 'size', v))
        
        b1 = ARButton(text="ملخص المدفوعات", background_color=(0.15, 0.15, 0.15, 1),
                      color=(1, 1, 1, 1), size_hint_y=None, height=dp(44))
        b1.bind(on_release=lambda x: setattr(self.manager, 'current', 'summary'))
        btns_box.add_widget(b1)
        
        b3 = ARButton(text="الإعدادات", background_color=(0.5, 0.5, 0.5, 1),
                      color=(1, 1, 1, 1), size_hint_y=None, height=dp(44))
        b3.bind(on_release=lambda x: setattr(self.manager, 'current', 'settings'))
        btns_box.add_widget(b3)
        
        content.add_widget(btns_box)
        
        # Developer
        dev = ARLabel(text=f"بواسطة {PROJECT['developer']}", font_size='11sp',
                      color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(25))
        content.add_widget(dev)
        
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def make_brother_row(self, bid):
        row = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(12))
        
        # background
        with row.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(10)])
        row.bind(pos=lambda i, v, r=rect: setattr(r, 'pos', v),
                 size=lambda i, v, r=rect: setattr(r, 'size', v))
        
        info = BoxLayout(orientation='vertical', size_hint_x=0.6)
        name_lbl = ARLabel(text="---", bold=True, font_size='15sp',
                          color=(0.1, 0.1, 0.1, 1), halign='right')
        paid_lbl = ARLabel(text="المدفوع: 0", font_size='12sp',
                          color=(0.12, 0.52, 0.3, 1), halign='right')
        info.add_widget(name_lbl)
        info.add_widget(paid_lbl)
        
        rem_lbl = ARLabel(text="المتبقي: 0", font_size='12sp',
                         color=(0.78, 0.18, 0.18, 1), size_hint_x=0.25)
        
        btn = ARButton(text="تفاصيل", size_hint_x=0.15,
                      background_color=(0.2, 0.5, 0.7, 1), color=(1, 1, 1, 1))
        btn.bind(on_release=lambda x, b=bid: self.open_detail(b))
        
        row.add_widget(info)
        row.add_widget(rem_lbl)
        row.add_widget(btn)
        
        self.brother_labels[bid] = (name_lbl, paid_lbl, rem_lbl)
        return row

    def open_detail(self, bid):
        app = App.get_running_app()
        app.selected_bid = bid
        self.manager.get_screen('detail').load(bid)
        self.manager.current = 'detail'

    def on_enter(self):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        db = app.db
        self.tp_lbl.set_text(f"إجمالي المدفوع: {db.total_paid():,.0f} دينار")
        self.tr_lbl.set_text(f"إجمالي المتبقي: {db.total_remaining():,.0f} دينار")
        
        for bid, (n, p, r) in self.brother_labels.items():
            n.set_text(db.name(bid))
            p.set_text(f"المدفوع: {db.paid(bid):,.0f}")
            r.set_text(f"المتبقي: {db.remaining(bid):,.0f}")


class DetailScreen(Screen):
    _bid = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=dp(8))
        with header.canvas.before:
            Color(1, 1, 1, 1)
            self.hrect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(self.hrect, 'pos', v),
                    size=lambda i, v: setattr(self.hrect, 'size', v))
        
        back = Button(text="<", size_hint_x=None, width=dp(50),
                     background_color=(0.9, 0.9, 0.9, 1), color=(0, 0, 0, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back)
        
        self.title_lbl = ARLabel(text="تفاصيل", bold=True, font_size='18sp',
                                 color=(0.1, 0.1, 0.1, 1))
        header.add_widget(self.title_lbl)
        header.add_widget(Label(size_hint_x=None, width=dp(50)))
        root.add_widget(header)
        
        # Content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10),
                          size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Info card
        info = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(160),
                        padding=dp(14))
        with info.canvas.before:
            Color(1, 1, 1, 1)
            self.irect = RoundedRectangle(pos=info.pos, size=info.size, radius=[dp(10)])
        info.bind(pos=lambda i, v: setattr(self.irect, 'pos', v),
                  size=lambda i, v: setattr(self.irect, 'size', v))
        
        self.name_lbl = ARLabel(text="---", bold=True, font_size='20sp',
                               color=(0.1, 0.1, 0.1, 1), size_hint_y=None,
                               height=dp(32), halign='right')
        info.add_widget(self.name_lbl)
        
        self.share_lbl = ARLabel(text="---", font_size='13sp',
                                color=(0.5, 0.5, 0.5, 1), size_hint_y=None,
                                height=dp(24), halign='right')
        info.add_widget(self.share_lbl)
        
        self.paid_lbl = ARLabel(text="المدفوع: 0", bold=True, font_size='14sp',
                               color=(0.12, 0.52, 0.3, 1), size_hint_y=None,
                               height=dp(26), halign='right')
        info.add_widget(self.paid_lbl)
        
        self.rem_lbl = ARLabel(text="المتبقي: 0", bold=True, font_size='14sp',
                              color=(0.78, 0.18, 0.18, 1), size_hint_y=None,
                              height=dp(26), halign='right')
        info.add_widget(self.rem_lbl)
        
        content.add_widget(info)
        
        # Action buttons
        actions = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        add_btn = ARButton(text="إضافة دفعة", background_color=(0.12, 0.52, 0.3, 1),
                          color=(1, 1, 1, 1))
        add_btn.bind(on_release=self.add_payment_popup)
        actions.add_widget(add_btn)
        
        del_btn = ARButton(text="حذف آخر دفعة", background_color=(0.75, 0.18, 0.18, 1),
                          color=(1, 1, 1, 1))
        del_btn.bind(on_release=self.delete_last)
        actions.add_widget(del_btn)
        
        content.add_widget(actions)
        
        # Payments log
        content.add_widget(ARLabel(text="سجل الدفعات", bold=True, font_size='15sp',
                                    color=(0.3, 0.3, 0.3, 1), size_hint_y=None,
                                    height=dp(30), halign='right'))
        
        self.payments_box = BoxLayout(orientation='vertical', spacing=dp(6),
                                      size_hint_y=None)
        self.payments_box.bind(minimum_height=self.payments_box.setter('height'))
        content.add_widget(self.payments_box)
        
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def load(self, bid):
        self._bid = bid
        app = App.get_running_app()
        db = app.db
        name = db.name(bid)
        self.title_lbl.set_text(name)
        self.name_lbl.set_text(name)
        area = PROJECT["total_area_m2"] / 5
        self.share_lbl.set_text(f"الحصة: {area:.0f} م² | المطلوب: {PROJECT['share_price']:,}")
        self.paid_lbl.set_text(f"المدفوع: {db.paid(bid):,.0f} دينار")
        self.rem_lbl.set_text(f"المتبقي: {db.remaining(bid):,.0f} دينار")
        
        self.payments_box.clear_widgets()
        pays = db.payments(bid)
        if not pays:
            lbl = ARLabel(text="لا توجد دفعات", color=(0.6, 0.6, 0.6, 1),
                         size_hint_y=None, height=dp(50))
            self.payments_box.add_widget(lbl)
        else:
            for p in reversed(pays):
                self.payments_box.add_widget(self.make_pay_card(p))

    def make_pay_card(self, p):
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(90),
                        padding=dp(10))
        with card.canvas.before:
            Color(0.97, 0.97, 0.97, 1)
            rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
        card.bind(pos=lambda i, v, r=rect: setattr(r, 'pos', v),
                  size=lambda i, v, r=rect: setattr(r, 'size', v))
        
        card.add_widget(ARLabel(text=f"{p['amount']:,.0f} دينار", bold=True,
                                font_size='15sp', color=(0.12, 0.52, 0.3, 1),
                                size_hint_y=None, height=dp(24), halign='right'))
        card.add_widget(ARLabel(text=f"التاريخ: {p['date']}", font_size='11sp',
                                color=(0.4, 0.4, 0.4, 1), size_hint_y=None,
                                height=dp(20), halign='right'))
        
        note_txt = p.get('note', '') or 'بدون ملاحظة'
        bank_txt = p.get('bank', '')
        display = f"{note_txt}"
        if bank_txt:
            display = f"{bank_txt} | {note_txt}"
        card.add_widget(ARLabel(text=display, font_size='11sp',
                                color=(0.5, 0.5, 0.5, 1), size_hint_y=None,
                                height=dp(20), halign='right'))
        return card

    def add_payment_popup(self, *a):
        app = App.get_running_app()
        db = app.db
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        amount = TextInput(hint_text="المبلغ", input_filter='float', multiline=False,
                          size_hint_y=None, height=dp(45))
        content.add_widget(amount)
        
        date = TextInput(hint_text=f"التاريخ (فارغ = اليوم)", multiline=False,
                        size_hint_y=None, height=dp(45))
        content.add_widget(date)
        
        bank = Spinner(text=AR("اختر البنك"), values=[AR(b) for b in BANKS],
                      size_hint_y=None, height=dp(45), font_name='Arabic')
        content.add_widget(bank)
        
        note = TextInput(hint_text="ملاحظة", multiline=True,
                        size_hint_y=None, height=dp(80))
        content.add_widget(note)
        
        btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        
        popup = Popup(title=AR(f"إضافة دفعة - {db.name(self._bid)}"),
                     content=content, size_hint=(0.9, 0.8), title_font='Arabic')
        
        def save(*args):
            try:
                a = float(amount.text.strip())
                if a <= 0:
                    return
            except:
                return
            d = date.text.strip() or datetime.now().strftime("%Y-%m-%d")
            b_txt = bank.text if bank.text != AR("اختر البنك") else ""
            db.add_payment(self._bid, a, d, note.text.strip(), b_txt)
            popup.dismiss()
            self.load(self._bid)
        
        save_btn = ARButton(text="حفظ", background_color=(0.12, 0.52, 0.3, 1),
                           color=(1, 1, 1, 1))
        save_btn.bind(on_release=save)
        btns.add_widget(save_btn)
        
        cancel_btn = ARButton(text="إلغاء", background_color=(0.6, 0.6, 0.6, 1),
                             color=(1, 1, 1, 1))
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        btns.add_widget(cancel_btn)
        
        content.add_widget(btns)
        popup.open()

    def delete_last(self, *a):
        app = App.get_running_app()
        if app.db.delete_last(self._bid):
            self.load(self._bid)


class SummaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation='vertical')
        
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=dp(8))
        with header.canvas.before:
            Color(1, 1, 1, 1)
            self.hrect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(self.hrect, 'pos', v),
                    size=lambda i, v: setattr(self.hrect, 'size', v))
        
        back = Button(text="<", size_hint_x=None, width=dp(50),
                     background_color=(0.9, 0.9, 0.9, 1), color=(0, 0, 0, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back)
        header.add_widget(ARLabel(text="ملخص المدفوعات", bold=True, font_size='18sp',
                                 color=(0.1, 0.1, 0.1, 1)))
        header.add_widget(Label(size_hint_x=None, width=dp(50)))
        root.add_widget(header)
        
        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10),
                                size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        app = App.get_running_app()
        db = app.db
        self.content.clear_widgets()
        
        # Total
        total_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100),
                              padding=dp(14))
        with total_card.canvas.before:
            Color(1, 1, 1, 1)
            r = RoundedRectangle(pos=total_card.pos, size=total_card.size, radius=[dp(10)])
        total_card.bind(pos=lambda i, v: setattr(r, 'pos', v),
                        size=lambda i, v: setattr(r, 'size', v))
        
        total_card.add_widget(ARLabel(text="الإجمالي العام", bold=True, font_size='15sp',
                                      color=(0.1, 0.1, 0.1, 1), size_hint_y=None,
                                      height=dp(26), halign='right'))
        total_card.add_widget(ARLabel(text=f"المدفوع: {db.total_paid():,.0f}",
                                      color=(0.12, 0.52, 0.3, 1), bold=True,
                                      size_hint_y=None, height=dp(24), halign='right'))
        total_card.add_widget(ARLabel(text=f"المتبقي: {db.total_remaining():,.0f}",
                                      color=(0.78, 0.18, 0.18, 1), bold=True,
                                      size_hint_y=None, height=dp(24), halign='right'))
        self.content.add_widget(total_card)
        
        # Each brother
        for i in range(1, 6):
            name = db.name(i)
            paid = db.paid(i)
            rem = db.remaining(i)
            cnt = len(db.payments(i))
            pct = (paid / PROJECT["share_price"] * 100) if PROJECT["share_price"] else 0
            
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(110),
                            padding=dp(12))
            with card.canvas.before:
                Color(1, 1, 1, 1)
                rec = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
            card.bind(pos=lambda i, v, r=rec: setattr(r, 'pos', v),
                      size=lambda i, v, r=rec: setattr(r, 'size', v))
            
            card.add_widget(ARLabel(text=name, bold=True, font_size='14sp',
                                    color=(0.1, 0.1, 0.1, 1), size_hint_y=None,
                                    height=dp(24), halign='right'))
            card.add_widget(ARLabel(text=f"المدفوع: {paid:,.0f} | المتبقي: {rem:,.0f}",
                                    font_size='11sp', color=(0.4, 0.4, 0.4, 1),
                                    size_hint_y=None, height=dp(22), halign='right'))
            card.add_widget(ARLabel(text=f"عدد الدفعات: {cnt} | النسبة: {pct:.0f}%",
                                    font_size='11sp', color=(0.5, 0.5, 0.5, 1),
                                    size_hint_y=None, height=dp(22), halign='right'))
            self.content.add_widget(card)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation='vertical')
        
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=dp(8))
        with header.canvas.before:
            Color(1, 1, 1, 1)
            self.hrect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(self.hrect, 'pos', v),
                    size=lambda i, v: setattr(self.hrect, 'size', v))
        
        back = Button(text="<", size_hint_x=None, width=dp(50),
                     background_color=(0.9, 0.9, 0.9, 1), color=(0, 0, 0, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back)
        header.add_widget(ARLabel(text="الإعدادات", bold=True, font_size='18sp',
                                 color=(0.1, 0.1, 0.1, 1)))
        header.add_widget(Label(size_hint_x=None, width=dp(50)))
        root.add_widget(header)
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12),
                          size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        content.add_widget(ARLabel(text="تعديل أسماء الإخوة", bold=True, font_size='15sp',
                                    color=(0.2, 0.2, 0.2, 1), size_hint_y=None,
                                    height=dp(30), halign='right'))
        
        self.name_inputs = {}
        for i in range(1, 6):
            ti = TextInput(hint_text=f"اسم الأخ {i}", multiline=False,
                          size_hint_y=None, height=dp(46), font_name='Arabic')
            content.add_widget(ti)
            self.name_inputs[i] = ti
        
        save_btn = ARButton(text="حفظ الأسماء", background_color=(0.12, 0.52, 0.3, 1),
                           color=(1, 1, 1, 1), size_hint_y=None, height=dp(48))
        save_btn.bind(on_release=self.save_names)
        content.add_widget(save_btn)
        
        # Password
        content.add_widget(ARLabel(text="كلمة السر", bold=True, font_size='15sp',
                                    color=(0.2, 0.2, 0.2, 1), size_hint_y=None,
                                    height=dp(30), halign='right'))
        
        self.pw_input = TextInput(hint_text="كلمة سر جديدة", password=True,
                                  multiline=False, size_hint_y=None, height=dp(46))
        content.add_widget(self.pw_input)
        
        pw_btn = ARButton(text="تعيين كلمة السر", background_color=(0.2, 0.45, 0.7, 1),
                         color=(1, 1, 1, 1), size_hint_y=None, height=dp(44))
        pw_btn.bind(on_release=self.set_pw)
        content.add_widget(pw_btn)
        
        rm_btn = ARButton(text="إزالة كلمة السر", background_color=(0.8, 0.5, 0.1, 1),
                         color=(1, 1, 1, 1), size_hint_y=None, height=dp(44))
        rm_btn.bind(on_release=self.remove_pw)
        content.add_widget(rm_btn)
        
        content.add_widget(Label(size_hint_y=None, height=dp(20)))
        
        reset_btn = ARButton(text="إعادة تعيين البيانات", background_color=(0.75, 0.18, 0.18, 1),
                            color=(1, 1, 1, 1), size_hint_y=None, height=dp(48))
        reset_btn.bind(on_release=self.reset_data)
        content.add_widget(reset_btn)
        
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        app = App.get_running_app()
        for i in range(1, 6):
            self.name_inputs[i].text = app.db.name(i)

    def save_names(self, *a):
        app = App.get_running_app()
        for i in range(1, 6):
            n = self.name_inputs[i].text.strip()
            if n:
                app.db.set_name(i, n)

    def set_pw(self, *a):
        pw = self.pw_input.text.strip()
        if pw:
            App.get_running_app().db.set_password(pw)
            self.pw_input.text = ""

    def remove_pw(self, *a):
        App.get_running_app().db.remove_password()

    def reset_data(self, *a):
        App.get_running_app().db.reset()
        self.on_enter()


# ============================================================
# التطبيق
# ============================================================
class LandApp(App):
    def build(self):
        self.title = "Ard Alekhwa"
        self.db = DB()
        self.selected_bid = 0
        Window.clearcolor = (0.96, 0.96, 0.96, 1)
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(DetailScreen(name='detail'))
        sm.add_widget(SummaryScreen(name='summary'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm


if __name__ == '__main__':
    LandApp().run()
