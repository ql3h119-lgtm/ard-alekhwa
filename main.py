# main.py
# أرض الإخوة - إدارة شراء الأرض
# بواسطة Abu Jabr
# مساحة الأرض: 2506 متر مربع

import json
import os
import shutil
import hashlib
from datetime import datetime, timedelta

APP_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(APP_DIR, "arabic.ttf")
DATA_FILE = os.path.join(APP_DIR, "land_data.json")
BACKUP_DIR = os.path.join(APP_DIR, "backups")

if not os.path.exists(FONT_PATH):
    for wf in [r"C:\Windows\Fonts\tahoma.ttf",
               r"C:\Windows\Fonts\arial.ttf",
               r"C:\Windows\Fonts\segoeui.ttf"]:
        if os.path.exists(wf):
            shutil.copy(wf, FONT_PATH)
            break

from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu

if os.path.exists(FONT_PATH):
    LabelBase.register(name="Arabic", fn_regular=FONT_PATH)
    LabelBase.register(name="Roboto", fn_regular=FONT_PATH)

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RESHAPER = True
except ImportError:
    HAS_RESHAPER = False

def AR(text):
    if HAS_RESHAPER and text:
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except:
            return str(text)
    return str(text)

Window.size = (400, 780)

# ============================================================
# إعدادات المشروع - أرض الإخوة
# ============================================================
PROJECT = {
    "app_name": "أرض الإخوة",
    "total_area_m2": 2506,
    "total_area_dunum": 2.506,
    "total_price": 35000,
    "brothers_count": 5,
    "share_price": 7000,
    "monthly": 1000,
    "developer": "Abu Jabr",
}

# البنوك الفلسطينية والأردنية
BANKS = [
    "البنك العربي",
    "بنك فلسطين",
    "بنك القدس",
    "البنك الإسلامي العربي",
    "البنك الوطني",
    "بنك الأردن",
    "البنك الأهلي الأردني",
    "بنك الإسكان",
    "بنك القاهرة عمان",
    "البنك التجاري الأردني",
    "بنك الاستثمار الفلسطيني",
    "بنك الإنتاج",
    "كاش / نقدي",
    "حوالة",
    "أخرى",
]


# ============================================================
# قاعدة البيانات
# ============================================================
class DB:
    # ====== غيّر الأسماء هنا ======
    DEFAULT_NAMES = {
        1: "الأخ الأول",
        2: "الأخ الثاني",
        3: "الأخ الثالث",
        4: "الأخ الرابع",
        5: "الأخ الخامس",
    }
    # ================================

    def __init__(self):
        self.data = self._load()
        self._ensure_fields()

    def _default(self):
        d = {
            "password": "",
            "brothers": {},
        }
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
            # تأكد كل دفعة فيها حقل bank
            for p in b.get("payments", []):
                if "bank" not in p:
                    p["bank"] = ""
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
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        self._auto_backup()

    def _auto_backup(self):
        """نسخة احتياطية تلقائية"""
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        date_str = datetime.now().strftime("%Y%m%d")
        backup_file = os.path.join(BACKUP_DIR, f"backup_{date_str}.json")
        try:
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except:
            pass
        # حذف النسخ القديمة (أكثر من 30 يوم)
        try:
            for fname in os.listdir(BACKUP_DIR):
                fpath = os.path.join(BACKUP_DIR, fname)
                age = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(fpath))).days
                if age > 30:
                    os.remove(fpath)
        except:
            pass

    def export_backup(self):
        """تصدير نسخة احتياطية يدوية"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = os.path.join(APP_DIR, f"backup_manual_{ts}.json")
        try:
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return export_file
        except:
            return None

    def import_backup(self, filepath):
        """استيراد نسخة احتياطية"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                imported = json.load(f)
            if "brothers" in imported:
                self.data = imported
                self.save()
                return True
        except:
            pass
        return False

    # كلمة السر
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

    # بيانات الإخوة
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

    def add_payment(self, bid, amount, date, note, bank="", pay_type=""):
        self.data["brothers"][str(bid)]["payments"].append({
            "amount": float(amount),
            "date": date,
            "note": note,
            "bank": bank,
            "type": pay_type,
        })
        try:
            cur = datetime.strptime(self.data["brothers"][str(bid)]["next_date"], "%Y-%m-%d")
            nxt = (cur.replace(day=1) + timedelta(days=32)).replace(day=1)
            self.data["brothers"][str(bid)]["next_date"] = nxt.strftime("%Y-%m-%d")
        except:
            pass
        self.save()

    def edit_payment_note(self, bid, index, new_note):
        pays = self.payments(bid)
        if 0 <= index < len(pays):
            pays[index]["note"] = new_note
            self.save()
            return True
        return False

    def delete_payment(self, bid, index):
        pays = self.payments(bid)
        if 0 <= index < len(pays):
            pays.pop(index)
            self.save()
            return True
        return False

    def delete_last(self, bid):
        p = self.payments(bid)
        if p:
            p.pop()
            self.save()
            return True
        return False

    def upcoming(self, days=7):
        result, now = [], datetime.now()
        for i in range(1, 6):
            try:
                nd = datetime.strptime(self.data["brothers"][str(i)]["next_date"], "%Y-%m-%d")
                diff = (nd - now).days
                if 0 <= diff <= days:
                    result.append({
                        "bid": i, "name": self.name(i),
                        "date": self.data["brothers"][str(i)]["next_date"],
                        "days": diff, "remaining": self.remaining(i),
                    })
            except:
                pass
        return result

    def reset(self):
        self.data = self._default()
        self.save()


# ============================================================
# KV Layout
# ============================================================
KV = """
# ====== شاشة كلمة السر ======
<LoginScreen>:
    name: "login"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 1, 1, 1, 1
        padding: "30dp"
        spacing: "20dp"

        Widget:
            size_hint_y: 0.15

        MDLabel:
            id: lg_title
            halign: "center"
            bold: True
            font_style: "H5"
            theme_text_color: "Custom"
            text_color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: "40dp"

        MDLabel:
            id: lg_sub
            halign: "center"
            font_style: "Body2"
            theme_text_color: "Custom"
            text_color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: "24dp"

        MDLabel:
            id: lg_area
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.6, 0.6, 0.6, 1
            size_hint_y: None
            height: "20dp"

        Widget:
            size_hint_y: 0.05

        MDTextField:
            id: lg_pass
            hint_text: "Password"
            password: True
            mode: "rectangle"
            size_hint_y: None
            height: "48dp"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5}
            on_text_validate: root.try_login()

        MDRaisedButton:
            id: lg_btn
            size_hint_x: 0.8
            size_hint_y: None
            height: "48dp"
            pos_hint: {"center_x": 0.5}
            md_bg_color: 0.15, 0.15, 0.15, 1
            elevation: 0
            on_release: root.try_login()

        MDLabel:
            id: lg_err
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.78, 0.18, 0.18, 1
            size_hint_y: None
            height: "24dp"

        Widget:

        MDLabel:
            id: lg_dev
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.75, 0.75, 0.75, 1
            size_hint_y: None
            height: "20dp"


# ====== الشاشة الرئيسية ======
<HomeScreen>:
    name: "home"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.96, 0.96, 0.96, 1
        MDBoxLayout:
            size_hint_y: None
            height: "62dp"
            md_bg_color: 1, 1, 1, 1
            padding: "10dp"
            MDLabel:
                id: hdr
                halign: "center"
                bold: True
                font_style: "H5"
                theme_text_color: "Custom"
                text_color: 0.1, 0.1, 0.1, 1
        MDBoxLayout:
            size_hint_y: None
            height: "1dp"
            md_bg_color: 0.88, 0.88, 0.88, 1
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "14dp"
                spacing: "10dp"
                adaptive_height: True

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "195dp"
                    padding: "14dp"
                    spacing: "5dp"
                    radius: [12]
                    elevation: 1
                    md_bg_color: 1, 1, 1, 1
                    MDLabel:
                        id: pt
                        halign: "right"
                        bold: True
                        font_style: "Subtitle1"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        size_hint_y: None
                        height: "26dp"
                    MDBoxLayout:
                        size_hint_y: None
                        height: "1dp"
                        md_bg_color: 0.9, 0.9, 0.9, 1
                    MDLabel:
                        id: i1
                        halign: "right"
                        font_style: "Body2"
                        theme_text_color: "Custom"
                        text_color: 0.4, 0.4, 0.4, 1
                        size_hint_y: None
                        height: "22dp"
                    MDLabel:
                        id: i2
                        halign: "right"
                        font_style: "Body2"
                        theme_text_color: "Custom"
                        text_color: 0.4, 0.4, 0.4, 1
                        size_hint_y: None
                        height: "22dp"
                    MDLabel:
                        id: i3
                        halign: "right"
                        font_style: "Body2"
                        theme_text_color: "Custom"
                        text_color: 0.4, 0.4, 0.4, 1
                        size_hint_y: None
                        height: "22dp"
                    MDLabel:
                        id: tp
                        halign: "right"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.12, 0.52, 0.3, 1
                        size_hint_y: None
                        height: "24dp"
                    MDLabel:
                        id: tr
                        halign: "right"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.78, 0.18, 0.18, 1
                        size_hint_y: None
                        height: "24dp"

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "54dp"
                    padding: "14dp"
                    radius: [10]
                    elevation: 1
                    md_bg_color: 1, 1, 1, 1
                    MDLabel:
                        id: alrt
                        halign: "right"
                        font_style: "Body2"
                        theme_text_color: "Custom"
                        text_color: 0.12, 0.52, 0.3, 1

                MDLabel:
                    id: bt
                    halign: "right"
                    bold: True
                    font_style: "Subtitle2"
                    size_hint_y: None
                    height: "28dp"
                    theme_text_color: "Custom"
                    text_color: 0.3, 0.3, 0.3, 1

                BrotherRow:
                    bid: 1
                BrotherRow:
                    bid: 2
                BrotherRow:
                    bid: 3
                BrotherRow:
                    bid: 4
                BrotherRow:
                    bid: 5

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "250dp"
                    padding: "12dp"
                    spacing: "8dp"
                    radius: [12]
                    elevation: 1
                    md_bg_color: 1, 1, 1, 1
                    MDRaisedButton:
                        id: b1
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        elevation: 0
                        on_release: root.go("summary")
                    MDRaisedButton:
                        id: b2
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        elevation: 0
                        on_release: root.go("alerts")
                    MDRaisedButton:
                        id: b4
                        size_hint_x: 1
                        md_bg_color: 0.2, 0.45, 0.7, 1
                        elevation: 0
                        on_release: root.do_backup()
                    MDRaisedButton:
                        id: b3
                        size_hint_x: 1
                        md_bg_color: 0.5, 0.5, 0.5, 1
                        elevation: 0
                        on_release: root.go("settings")

                MDLabel:
                    id: dev_label
                    halign: "center"
                    font_style: "Caption"
                    theme_text_color: "Custom"
                    text_color: 0.75, 0.75, 0.75, 1
                    size_hint_y: None
                    height: "22dp"


<BrotherRow>:
    size_hint_y: None
    height: "78dp"
    radius: [10]
    elevation: 1
    padding: "14dp"
    md_bg_color: 1, 1, 1, 1
    ripple_behavior: True
    on_release: root.open_detail()
    MDBoxLayout:
        orientation: "horizontal"
        MDBoxLayout:
            orientation: "vertical"
            size_hint_x: 0.6
            MDLabel:
                id: rn
                halign: "right"
                bold: True
                font_style: "Subtitle1"
                theme_text_color: "Custom"
                text_color: 0.1, 0.1, 0.1, 1
                size_hint_y: None
                height: "26dp"
            MDLabel:
                id: rp
                halign: "right"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.12, 0.52, 0.3, 1
                size_hint_y: None
                height: "20dp"
        MDBoxLayout:
            orientation: "vertical"
            size_hint_x: 0.4
            MDLabel:
                id: rr
                halign: "center"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.78, 0.18, 0.18, 1
                size_hint_y: None
                height: "22dp"
            MDLabel:
                id: rm
                halign: "center"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.65, 0.65, 0.65, 1
                size_hint_y: None
                height: "20dp"


<DetailScreen>:
    name: "detail"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.96, 0.96, 0.96, 1
        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 1, 1, 1, 1
            MDIconButton:
                icon: "arrow-right"
                on_release: root.back()
            MDLabel:
                id: dt
                halign: "center"
                bold: True
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0.1, 0.1, 0.1, 1
            Widget:
                size_hint_x: None
                width: "48dp"
        MDBoxLayout:
            size_hint_y: None
            height: "1dp"
            md_bg_color: 0.88, 0.88, 0.88, 1
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "14dp"
                spacing: "10dp"
                adaptive_height: True

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "160dp"
                    padding: "14dp"
                    spacing: "4dp"
                    radius: [12]
                    elevation: 1
                    md_bg_color: 1, 1, 1, 1
                    MDLabel:
                        id: dn
                        halign: "right"
                        bold: True
                        font_style: "H6"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        size_hint_y: None
                        height: "30dp"
                    MDBoxLayout:
                        size_hint_y: None
                        height: "1dp"
                        md_bg_color: 0.9, 0.9, 0.9, 1
                    MDLabel:
                        id: ds
                        halign: "right"
                        font_style: "Body2"
                        theme_text_color: "Custom"
                        text_color: 0.45, 0.45, 0.45, 1
                        size_hint_y: None
                        height: "22dp"
                    MDLabel:
                        id: dp1
                        halign: "right"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.12, 0.52, 0.3, 1
                        size_hint_y: None
                        height: "24dp"
                    MDLabel:
                        id: dr
                        halign: "right"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.78, 0.18, 0.18, 1
                        size_hint_y: None
                        height: "24dp"
                    MDLabel:
                        id: dnx
                        halign: "right"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.5, 0.5, 0.5, 1
                        size_hint_y: None
                        height: "20dp"

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "155dp"
                    padding: "12dp"
                    spacing: "6dp"
                    radius: [12]
                    elevation: 1
                    md_bg_color: 1, 0.99, 0.94, 1
                    MDBoxLayout:
                        size_hint_y: None
                        height: "28dp"
                        MDLabel:
                            id: nt_title
                            halign: "right"
                            bold: True
                            font_style: "Subtitle2"
                            theme_text_color: "Custom"
                            text_color: 0.4, 0.35, 0.1, 1
                        MDIconButton:
                            icon: "pencil"
                            theme_text_color: "Custom"
                            text_color: 0.4, 0.35, 0.1, 1
                            size_hint_x: None
                            width: "40dp"
                            on_release: root.edit_notes()
                    MDBoxLayout:
                        size_hint_y: None
                        height: "1dp"
                        md_bg_color: 0.9, 0.85, 0.7, 1
                    ScrollView:
                        MDLabel:
                            id: nt_text
                            halign: "right"
                            font_style: "Body2"
                            theme_text_color: "Custom"
                            text_color: 0.35, 0.3, 0.15, 1
                            valign: "top"
                            text_size: self.width, None
                            padding: "4dp", "4dp"

                MDBoxLayout:
                    size_hint_y: None
                    height: "48dp"
                    spacing: "10dp"
                    MDRaisedButton:
                        id: ba
                        size_hint_x: 0.5
                        md_bg_color: 0.12, 0.52, 0.3, 1
                        elevation: 0
                        on_release: root.go_add()
                    MDRaisedButton:
                        id: bd
                        size_hint_x: 0.5
                        md_bg_color: 0.75, 0.18, 0.18, 1
                        elevation: 0
                        on_release: root.ask_del()

                MDLabel:
                    id: dlt
                    halign: "right"
                    bold: True
                    font_style: "Subtitle2"
                    size_hint_y: None
                    height: "28dp"
                    theme_text_color: "Custom"
                    text_color: 0.3, 0.3, 0.3, 1

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "380dp"
                    padding: "10dp"
                    radius: [12]
                    elevation: 1
                    md_bg_color: 1, 1, 1, 1
                    ScrollView:
                        MDBoxLayout:
                            id: dl
                            orientation: "vertical"
                            spacing: "8dp"
                            adaptive_height: True


<AddScreen>:
    name: "add"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.96, 0.96, 0.96, 1
        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 1, 1, 1, 1
            MDIconButton:
                icon: "arrow-right"
                on_release: root.back()
            MDLabel:
                id: at
                halign: "center"
                bold: True
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0.1, 0.1, 0.1, 1
            Widget:
                size_hint_x: None
                width: "48dp"
        MDBoxLayout:
            size_hint_y: None
            height: "1dp"
            md_bg_color: 0.88, 0.88, 0.88, 1
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "12dp"
                adaptive_height: True
                MDLabel:
                    id: al
                    halign: "right"
                    bold: True
                    font_style: "Subtitle1"
                    size_hint_y: None
                    height: "30dp"
                    theme_text_color: "Custom"
                    text_color: 0.15, 0.15, 0.15, 1
                MDTextField:
                    id: fa
                    hint_text: "Amount / المبلغ"
                    input_filter: "float"
                    mode: "rectangle"
                    size_hint_y: None
                    height: "48dp"
                MDTextField:
                    id: fd
                    hint_text: "Date YYYY-MM-DD / التاريخ"
                    mode: "rectangle"
                    size_hint_y: None
                    height: "48dp"

                # اختيار نوع الدفعة
                MDBoxLayout:
                    size_hint_y: None
                    height: "44dp"
                    spacing: "8dp"
                    MDRaisedButton:
                        id: bm
                        size_hint_x: 0.33
                        md_bg_color: 0.25, 0.25, 0.25, 1
                        elevation: 0
                        on_release: root.p_check()
                    MDRaisedButton:
                        id: bf
                        size_hint_x: 0.33
                        md_bg_color: 0.25, 0.25, 0.25, 1
                        elevation: 0
                        on_release: root.p_first()
                    MDRaisedButton:
                        id: bca
                        size_hint_x: 0.33
                        md_bg_color: 0.25, 0.25, 0.25, 1
                        elevation: 0
                        on_release: root.p_cash()

                # اختيار البنك
                MDRaisedButton:
                    id: bank_btn
                    size_hint_x: 1
                    size_hint_y: None
                    height: "44dp"
                    md_bg_color: 0.92, 0.92, 0.92, 1
                    theme_text_color: "Custom"
                    text_color: 0.2, 0.2, 0.2, 1
                    elevation: 0
                    on_release: root.show_banks()

                MDTextField:
                    id: fn
                    hint_text: "Note / ملاحظة الدفعة"
                    mode: "rectangle"
                    multiline: True
                    size_hint_y: None
                    height: "80dp"

                MDRaisedButton:
                    id: bc
                    size_hint_x: 1
                    size_hint_y: None
                    height: "50dp"
                    md_bg_color: 0.12, 0.52, 0.3, 1
                    elevation: 0
                    on_release: root.confirm()

                Widget:
                    size_hint_y: None
                    height: "20dp"


<SumScreen>:
    name: "summary"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.96, 0.96, 0.96, 1
        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 1, 1, 1, 1
            MDIconButton:
                icon: "arrow-right"
                on_release: root.back()
            MDLabel:
                id: st
                halign: "center"
                bold: True
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0.1, 0.1, 0.1, 1
            Widget:
                size_hint_x: None
                width: "48dp"
        MDBoxLayout:
            size_hint_y: None
            height: "1dp"
            md_bg_color: 0.88, 0.88, 0.88, 1
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "14dp"
                spacing: "10dp"
                adaptive_height: True
                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "110dp"
                    padding: "14dp"
                    spacing: "4dp"
                    radius: [12]
                    elevation: 1
                    md_bg_color: 1, 1, 1, 1
                    MDLabel:
                        id: sh
                        halign: "right"
                        bold: True
                        font_style: "Subtitle1"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        size_hint_y: None
                        height: "24dp"
                    MDBoxLayout:
                        size_hint_y: None
                        height: "1dp"
                        md_bg_color: 0.9, 0.9, 0.9, 1
                    MDLabel:
                        id: sp
                        halign: "right"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.12, 0.52, 0.3, 1
                        size_hint_y: None
                        height: "22dp"
                    MDLabel:
                        id: sr
                        halign: "right"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.78, 0.18, 0.18, 1
                        size_hint_y: None
                        height: "22dp"
                MDBoxLayout:
                    id: sl
                    orientation: "vertical"
                    spacing: "10dp"
                    adaptive_height: True


<AlertScreen>:
    name: "alerts"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.96, 0.96, 0.96, 1
        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 1, 1, 1, 1
            MDIconButton:
                icon: "arrow-right"
                on_release: root.back()
            MDLabel:
                id: at2
                halign: "center"
                bold: True
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0.1, 0.1, 0.1, 1
            Widget:
                size_hint_x: None
                width: "48dp"
        MDBoxLayout:
            size_hint_y: None
            height: "1dp"
            md_bg_color: 0.88, 0.88, 0.88, 1
        ScrollView:
            MDBoxLayout:
                id: ab
                orientation: "vertical"
                padding: "14dp"
                spacing: "10dp"
                adaptive_height: True


<SetScreen>:
    name: "settings"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.96, 0.96, 0.96, 1
        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 1, 1, 1, 1
            MDIconButton:
                icon: "arrow-right"
                on_release: root.back()
            MDLabel:
                id: st2
                halign: "center"
                bold: True
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0.1, 0.1, 0.1, 1
            Widget:
                size_hint_x: None
                width: "48dp"
        MDBoxLayout:
            size_hint_y: None
            height: "1dp"
            md_bg_color: 0.88, 0.88, 0.88, 1
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "12dp"
                adaptive_height: True

                MDLabel:
                    id: sh2
                    halign: "right"
                    bold: True
                    font_style: "Subtitle1"
                    size_hint_y: None
                    height: "30dp"
                    theme_text_color: "Custom"
                    text_color: 0.2, 0.2, 0.2, 1
                MDTextField:
                    id: s1
                    hint_text: "Name 1"
                    mode: "rectangle"
                    size_hint_y: None
                    height: "46dp"
                MDTextField:
                    id: s2
                    hint_text: "Name 2"
                    mode: "rectangle"
                    size_hint_y: None
                    height: "46dp"
                MDTextField:
                    id: s3
                    hint_text: "Name 3"
                    mode: "rectangle"
                    size_hint_y: None
                    height: "46dp"
                MDTextField:
                    id: s4
                    hint_text: "Name 4"
                    mode: "rectangle"
                    size_hint_y: None
                    height: "46dp"
                MDTextField:
                    id: s5
                    hint_text: "Name 5"
                    mode: "rectangle"
                    size_hint_y: None
                    height: "46dp"
                MDRaisedButton:
                    id: bs
                    size_hint_x: 1
                    size_hint_y: None
                    height: "48dp"
                    md_bg_color: 0.12, 0.52, 0.3, 1
                    elevation: 0
                    on_release: root.save()

                MDLabel:
                    id: pw_title
                    halign: "right"
                    bold: True
                    font_style: "Subtitle1"
                    size_hint_y: None
                    height: "30dp"
                    theme_text_color: "Custom"
                    text_color: 0.2, 0.2, 0.2, 1
                MDTextField:
                    id: pw_field
                    hint_text: "New Password"
                    password: True
                    mode: "rectangle"
                    size_hint_y: None
                    height: "46dp"
                MDRaisedButton:
                    id: pw_btn
                    size_hint_x: 1
                    size_hint_y: None
                    height: "44dp"
                    md_bg_color: 0.2, 0.45, 0.7, 1
                    elevation: 0
                    on_release: root.set_pw()
                MDRaisedButton:
                    id: pw_rm
                    size_hint_x: 1
                    size_hint_y: None
                    height: "44dp"
                    md_bg_color: 0.8, 0.5, 0.1, 1
                    elevation: 0
                    on_release: root.remove_pw()

                MDBoxLayout:
                    size_hint_y: None
                    height: "20dp"

                MDRaisedButton:
                    id: br
                    size_hint_x: 1
                    size_hint_y: None
                    height: "48dp"
                    md_bg_color: 0.75, 0.18, 0.18, 1
                    elevation: 0
                    on_release: root.ask_reset()
"""


def T(w, s):
    w.text = AR(s)


# ============================================================
# شاشة تسجيل الدخول
# ============================================================
class LoginScreen(Screen):
    def on_enter(self, *a):
        Clock.schedule_once(self._setup, 0)

    def _setup(self, dt):
        app = MDApp.get_running_app()
        db = app.db
        T(self.ids.lg_title, "أرض الإخوة")
        T(self.ids.lg_sub, "إدارة شراء الأرض المشتركة")
        T(self.ids.lg_area, f"المساحة: {PROJECT['total_area_m2']} م² | {PROJECT['total_area_dunum']} دونم")
        T(self.ids.lg_btn, "دخول")
        T(self.ids.lg_dev, f"بواسطة {PROJECT['developer']}")
        self.ids.lg_err.text = ""

        if not db.has_password():
            self.manager.current = "home"

    def try_login(self):
        app = MDApp.get_running_app()
        db = app.db
        pwd = self.ids.lg_pass.text.strip()

        if not db.has_password():
            self.manager.current = "home"
            return

        if db.check_password(pwd):
            self.ids.lg_pass.text = ""
            self.ids.lg_err.text = ""
            self.manager.current = "home"
        else:
            T(self.ids.lg_err, "كلمة السر خاطئة")


# ============================================================
# الشاشة الرئيسية
# ============================================================
class HomeScreen(Screen):
    def on_enter(self, *a):
        Clock.schedule_once(self.refresh, 0)

    def refresh(self, *a):
        app = MDApp.get_running_app()
        db = app.db
        T(self.ids.hdr, "أرض الإخوة")
        T(self.ids.pt, "معلومات المشروع")
        T(self.ids.i1, f"المساحة: {PROJECT['total_area_m2']} م² ({PROJECT['total_area_dunum']} دونم)")
        T(self.ids.i2, f"السعر الكلي: {PROJECT['total_price']:,.0f} دينار")
        T(self.ids.i3, f"عدد الإخوة: {PROJECT['brothers_count']}   |   حصة كل أخ: {PROJECT['share_price']:,.0f} دينار")
        T(self.ids.tp, f"إجمالي المدفوع: {db.total_paid():,.0f} دينار")
        T(self.ids.tr, f"إجمالي المتبقي: {db.total_remaining():,.0f} دينار")
        T(self.ids.bt, "الأقساط حسب كل أخ")
        T(self.ids.b1, "ملخص المدفوعات الكامل")
        T(self.ids.b2, "التنبيهات والمواعيد")
        T(self.ids.b4, "نسخة احتياطية")
        T(self.ids.b3, "الإعدادات")
        T(self.ids.dev_label, f"بواسطة {PROJECT['developer']}")

        up = db.upcoming(7)
        if up:
            n = " ، ".join(f"{u['name']} ({u['days']} يوم)" for u in up)
            T(self.ids.alrt, f"تنبيه: {n}")
            self.ids.alrt.text_color = (0.78, 0.18, 0.18, 1)
        else:
            T(self.ids.alrt, "لا توجد دفعات قادمة خلال أسبوع")
            self.ids.alrt.text_color = (0.12, 0.52, 0.3, 1)

        for w in self.walk():
            if isinstance(w, BrotherRow):
                w.refresh_row()

    def go(self, s):
        self.manager.current = s

    def do_backup(self):
        app = MDApp.get_running_app()
        path = app.db.export_backup()
        if path:
            Snackbar(text=AR(f"تم حفظ النسخة الاحتياطية")).open()
        else:
            Snackbar(text=AR("فشل حفظ النسخة")).open()


class BrotherRow(MDCard):
    bid = NumericProperty(0)

    def on_bid(self, *a):
        Clock.schedule_once(self.refresh_row, 0.05)

    def refresh_row(self, *a):
        app = MDApp.get_running_app()
        if not app or not hasattr(app, "db"):
            return
        db = app.db
        try:
            T(self.ids.rn, db.name(self.bid))
            T(self.ids.rp, f"المدفوع: {db.paid(self.bid):,.0f} دينار")
            T(self.ids.rr, f"المتبقي: {db.remaining(self.bid):,.0f}")
            T(self.ids.rm, "التفاصيل ←")
        except:
            pass

    def open_detail(self):
        app = MDApp.get_running_app()
        app.root.get_screen("detail").load(self.bid)
        app.root.current = "detail"


# ============================================================
# شاشة التفاصيل
# ============================================================
class DetailScreen(Screen):
    _bid = 0

    def load(self, bid):
        self._bid = bid
        Clock.schedule_once(self._do, 0)

    def _do(self, dt):
        app = MDApp.get_running_app()
        db = app.db
        bid = self._bid
        n = db.name(bid)
        T(self.ids.dt, n)
        T(self.ids.dn, n)
        area_each = PROJECT["total_area_m2"] / PROJECT["brothers_count"]
        T(self.ids.ds, f"الحصة: {area_each:.0f} م²   |   المطلوب: {PROJECT['share_price']:,.0f} دينار")
        T(self.ids.dp1, f"المدفوع: {db.paid(bid):,.0f} دينار")
        T(self.ids.dr, f"المتبقي: {db.remaining(bid):,.0f} دينار")
        nd = db.data["brothers"][str(bid)].get("next_date", "---")
        T(self.ids.dnx, f"الدفعة القادمة: {nd}")
        T(self.ids.ba, "إضافة دفعة")
        T(self.ids.bd, "حذف آخر دفعة")
        T(self.ids.dlt, "سجل الدفعات")
        T(self.ids.nt_title, "ملاحظات عامة")

        notes = db.notes(bid)
        if notes.strip():
            T(self.ids.nt_text, notes)
        else:
            T(self.ids.nt_text, "لا توجد ملاحظات - اضغط القلم للإضافة")

        self.ids.dl.clear_widgets()
        pays = db.payments(bid)
        if not pays:
            l = MDLabel(halign="center", font_style="Body2",
                        theme_text_color="Custom",
                        text_color=(0.6, 0.6, 0.6, 1),
                        size_hint_y=None, height=dp(50))
            T(l, "لا توجد دفعات مسجلة بعد")
            self.ids.dl.add_widget(l)
        else:
            for idx, p in list(enumerate(pays))[::-1]:
                note = p.get("note") or "بدون ملاحظة"
                bank = p.get("bank", "")
                pay_type = p.get("type", "")

                c = MDCard(orientation="vertical", size_hint_y=None,
                           height=dp(120), padding=dp(10), spacing=dp(2),
                           radius=[dp(8)], elevation=0,
                           md_bg_color=(0.97, 0.97, 0.97, 1))

                top = MDBoxLayout(size_hint_y=None, height=dp(28))
                btn_del = MDIconButton(
                    icon="delete-outline",
                    theme_text_color="Custom",
                    text_color=(0.75, 0.18, 0.18, 1),
                    size_hint_x=None, width=dp(36),
                    on_release=lambda x, i=idx: self.del_one(i))
                btn_edit = MDIconButton(
                    icon="pencil-outline",
                    theme_text_color="Custom",
                    text_color=(0.2, 0.4, 0.7, 1),
                    size_hint_x=None, width=dp(36),
                    on_release=lambda x, i=idx: self.edit_note(i))
                top.add_widget(btn_del)
                top.add_widget(btn_edit)
                l1 = MDLabel(halign="right", bold=True, font_style="Subtitle1",
                             theme_text_color="Custom",
                             text_color=(0.12, 0.52, 0.3, 1))
                T(l1, f"{p['amount']:,.0f} دينار")
                top.add_widget(l1)
                c.add_widget(top)

                l2 = MDLabel(halign="right", font_style="Caption",
                             theme_text_color="Custom",
                             text_color=(0.4, 0.4, 0.4, 1),
                             size_hint_y=None, height=dp(18))
                T(l2, f"التاريخ: {p['date']}")
                c.add_widget(l2)

                if bank:
                    lb = MDLabel(halign="right", font_style="Caption",
                                 theme_text_color="Custom",
                                 text_color=(0.2, 0.45, 0.7, 1),
                                 size_hint_y=None, height=dp(18))
                    type_text = f" ({pay_type})" if pay_type else ""
                    T(lb, f"البنك: {bank}{type_text}")
                    c.add_widget(lb)

                l3 = MDLabel(halign="right", font_style="Caption",
                             theme_text_color="Custom",
                             text_color=(0.5, 0.5, 0.5, 1),
                             size_hint_y=None, height=dp(30),
                             text_size=(dp(300), None))
                T(l3, note)
                c.add_widget(l3)
                self.ids.dl.add_widget(c)

    def edit_notes(self):
        app = MDApp.get_running_app()
        db = app.db
        box = MDBoxLayout(orientation="vertical", size_hint_y=None,
                          height=dp(180), spacing=dp(10))
        self._nf = MDTextField(text=db.notes(self._bid), multiline=True,
                               mode="rectangle", hint_text="ملاحظات...",
                               size_hint_y=None, height=dp(160))
        box.add_widget(self._nf)
        self._nd = MDDialog(
            title=AR("تعديل الملاحظات"), type="custom", content_cls=box,
            buttons=[
                MDFlatButton(text=AR("إلغاء"), on_release=lambda x: self._nd.dismiss()),
                MDRaisedButton(text=AR("حفظ"), md_bg_color=(0.12, 0.52, 0.3, 1),
                               on_release=lambda x: self._save_notes()),
            ])
        self._nd.open()

    def _save_notes(self):
        app = MDApp.get_running_app()
        app.db.set_notes(self._bid, self._nf.text.strip())
        self._nd.dismiss()
        self.load(self._bid)

    def edit_note(self, idx):
        app = MDApp.get_running_app()
        pays = app.db.payments(self._bid)
        if idx >= len(pays):
            return
        box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(150))
        self._pf = MDTextField(text=pays[idx].get("note", ""), multiline=True,
                               mode="rectangle", size_hint_y=None, height=dp(130))
        box.add_widget(self._pf)
        self._pi = idx
        self._pd = MDDialog(
            title=AR("تعديل الملاحظة"), type="custom", content_cls=box,
            buttons=[
                MDFlatButton(text=AR("إلغاء"), on_release=lambda x: self._pd.dismiss()),
                MDRaisedButton(text=AR("حفظ"), md_bg_color=(0.12, 0.52, 0.3, 1),
                               on_release=lambda x: self._save_pn()),
            ])
        self._pd.open()

    def _save_pn(self):
        app = MDApp.get_running_app()
        app.db.edit_payment_note(self._bid, self._pi, self._pf.text.strip())
        self._pd.dismiss()
        self.load(self._bid)

    def del_one(self, idx):
        app = MDApp.get_running_app()
        pays = app.db.payments(self._bid)
        if idx >= len(pays):
            return
        p = pays[idx]
        box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(50))
        l = MDLabel(halign="center", bold=True)
        T(l, f"{p['amount']:,.0f} دينار - {p['date']}")
        box.add_widget(l)
        self._di = idx
        self._dd = MDDialog(
            title=AR("حذف هذه الدفعة؟"), type="custom", content_cls=box,
            buttons=[
                MDFlatButton(text=AR("إلغاء"), on_release=lambda x: self._dd.dismiss()),
                MDRaisedButton(text=AR("حذف"), md_bg_color=(0.75, 0.18, 0.18, 1),
                               on_release=lambda x: self._do_del()),
            ])
        self._dd.open()

    def _do_del(self):
        app = MDApp.get_running_app()
        app.db.delete_payment(self._bid, self._di)
        self._dd.dismiss()
        self.load(self._bid)

    def go_add(self):
        app = MDApp.get_running_app()
        db = app.db
        s = self.manager.get_screen("add")
        s.target = self._bid
        s.selected_bank = ""
        s.pay_type = ""
        T(s.ids.at, "إضافة دفعة")
        T(s.ids.al, f"إضافة دفعة لـ: {db.name(self._bid)}")
        T(s.ids.bm, "شيك")
        T(s.ids.bf, "دفعة أولى")
        T(s.ids.bca, "كاش")
        T(s.ids.bank_btn, "اختر البنك")
        T(s.ids.bc, "تأكيد وحفظ الدفعة")
        s.ids.fa.text = ""
        s.ids.fd.text = ""
        s.ids.fn.text = ""
        self.manager.current = "add"

    def ask_del(self):
        app = MDApp.get_running_app()
        pays = app.db.payments(self._bid)
        if not pays:
            Snackbar(text=AR("لا توجد دفعات")).open()
            return
        last = pays[-1]
        box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(50))
        l = MDLabel(halign="center", bold=True)
        T(l, f"{last['amount']:,.0f} دينار - {last['date']}")
        box.add_widget(l)
        self._dd = MDDialog(
            title=AR("حذف آخر دفعة؟"), type="custom", content_cls=box,
            buttons=[
                MDFlatButton(text=AR("إلغاء"), on_release=lambda x: self._dd.dismiss()),
                MDRaisedButton(text=AR("حذف"), md_bg_color=(0.75, 0.18, 0.18, 1),
                               on_release=lambda x: self._do_del_last()),
            ])
        self._dd.open()

    def _do_del_last(self):
        app = MDApp.get_running_app()
        app.db.delete_last(self._bid)
        self._dd.dismiss()
        self.load(self._bid)

    def back(self):
        self.manager.current = "home"


# ============================================================
# شاشة إضافة دفعة
# ============================================================
class AddScreen(Screen):
    target = NumericProperty(0)
    selected_bank = ""
    pay_type = ""

    def p_check(self):
        self.ids.fa.text = "1000"
        self.ids.fn.text = "شيك شهري"
        self.pay_type = "شيك"

    def p_first(self):
        self.ids.fa.text = ""
        self.ids.fn.text = "دفعة أولى"
        self.pay_type = "دفعة أولى"

    def p_cash(self):
        self.ids.fa.text = ""
        self.ids.fn.text = "نقدي"
        self.selected_bank = "كاش / نقدي"
        self.pay_type = "كاش"
        T(self.ids.bank_btn, "كاش / نقدي")

    def show_banks(self):
        items = []
        for b in BANKS:
            items.append({
                "text": AR(b),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=b: self.pick_bank(x),
            })
        self._menu = MDDropdownMenu(
            caller=self.ids.bank_btn,
            items=items,
            width_mult=4,
        )
        self._menu.open()

    def pick_bank(self, bank_name):
        self.selected_bank = bank_name
        T(self.ids.bank_btn, bank_name)
        self._menu.dismiss()

    def confirm(self):
        amt = self.ids.fa.text.strip()
        date = self.ids.fd.text.strip()
        note = self.ids.fn.text.strip()
        if not amt:
            Snackbar(text=AR("أدخل المبلغ")).open()
            return
        try:
            a = float(amt)
            if a <= 0:
                raise ValueError
        except:
            Snackbar(text=AR("المبلغ غير صحيح")).open()
            return
        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except:
                Snackbar(text=AR("صيغة التاريخ خاطئة")).open()
                return
        else:
            date = datetime.now().strftime("%Y-%m-%d")

        app = MDApp.get_running_app()
        app.db.add_payment(self.target, a, date, note, self.selected_bank, self.pay_type)
        Snackbar(text=AR(f"تمت إضافة {a:,.0f} دينار")).open()
        self.manager.get_screen("detail").load(self.target)
        self.manager.current = "detail"

    def back(self):
        self.manager.current = "detail"


# ============================================================
# شاشة الملخص
# ============================================================
class SumScreen(Screen):
    def on_enter(self, *a):
        Clock.schedule_once(self._load, 0)

    def _load(self, dt):
        app = MDApp.get_running_app()
        db = app.db
        T(self.ids.st, "ملخص المدفوعات")
        T(self.ids.sh, "الإجمالي العام")
        T(self.ids.sp, f"المدفوع: {db.total_paid():,.0f} دينار")
        T(self.ids.sr, f"المتبقي: {db.total_remaining():,.0f} دينار")
        box = self.ids.sl
        box.clear_widgets()
        for i in range(1, 6):
            name = db.name(i)
            paid = db.paid(i)
            rem = db.remaining(i)
            cnt = len(db.payments(i))
            notes = db.notes(i)
            p = (paid / PROJECT["share_price"] * 100) if PROJECT["share_price"] else 0
            filled = int(p / 5)
            bar = "■" * filled + "□" * (20 - filled)
            clr = (0.12, 0.52, 0.3, 1) if p >= 50 else (0.8, 0.5, 0.1, 1)
            h = dp(140) if notes.strip() else dp(115)
            c = MDCard(orientation="vertical", size_hint_y=None, height=h,
                       padding=dp(12), spacing=dp(3), radius=[dp(12)], elevation=1,
                       md_bg_color=(1, 1, 1, 1))
            l1 = MDLabel(halign="right", bold=True, font_style="Subtitle1",
                         theme_text_color="Custom", text_color=(0.1, 0.1, 0.1, 1),
                         size_hint_y=None, height=dp(24))
            T(l1, name)
            c.add_widget(l1)
            l2 = MDLabel(halign="right", font_style="Body2",
                         theme_text_color="Custom", text_color=(0.4, 0.4, 0.4, 1),
                         size_hint_y=None, height=dp(22))
            T(l2, f"المدفوع: {paid:,.0f}  |  المتبقي: {rem:,.0f}  |  الدفعات: {cnt}")
            c.add_widget(l2)
            l3 = MDLabel(halign="right", font_style="Caption",
                         theme_text_color="Custom", text_color=clr,
                         size_hint_y=None, height=dp(20))
            T(l3, f"{bar}  {p:.0f}%")
            c.add_widget(l3)
            if notes.strip():
                l4 = MDLabel(halign="right", font_style="Caption",
                             theme_text_color="Custom", text_color=(0.4, 0.35, 0.1, 1),
                             size_hint_y=None, height=dp(22))
                T(l4, notes[:80])
                c.add_widget(l4)
            box.add_widget(c)

    def back(self):
        self.manager.current = "home"


class AlertScreen(Screen):
    def on_enter(self, *a):
        Clock.schedule_once(self._load, 0)

    def _load(self, dt):
        app = MDApp.get_running_app()
        db = app.db
        T(self.ids.at2, "التنبيهات والمواعيد")
        box = self.ids.ab
        box.clear_widgets()
        up = db.upcoming(30)
        if not up:
            c = MDCard(orientation="vertical", padding=dp(16),
                       size_hint_y=None, height=dp(64),
                       radius=[dp(12)], elevation=1, md_bg_color=(1, 1, 1, 1))
            l = MDLabel(halign="center", theme_text_color="Custom",
                        text_color=(0.12, 0.52, 0.3, 1))
            T(l, "لا توجد دفعات قادمة")
            c.add_widget(l)
            box.add_widget(c)
            return
        for u in up:
            if u["days"] <= 7:
                clr = (0.78, 0.18, 0.18, 1)
            elif u["days"] <= 14:
                clr = (0.78, 0.55, 0.1, 1)
            else:
                clr = (0.18, 0.4, 0.75, 1)
            c = MDCard(orientation="vertical", padding=dp(14), spacing=dp(4),
                       size_hint_y=None, height=dp(96),
                       radius=[dp(12)], elevation=1, md_bg_color=(1, 1, 1, 1))
            l1 = MDLabel(halign="right", bold=True, font_style="Subtitle1",
                         theme_text_color="Custom", text_color=clr,
                         size_hint_y=None, height=dp(24))
            T(l1, u["name"])
            c.add_widget(l1)
            l2 = MDLabel(halign="right", font_style="Body2",
                         theme_text_color="Custom", text_color=(0.4, 0.4, 0.4, 1),
                         size_hint_y=None, height=dp(22))
            T(l2, f"موعد الدفعة: {u['date']}   |   بعد {u['days']} يوم")
            c.add_widget(l2)
            l3 = MDLabel(halign="right", font_style="Caption",
                         theme_text_color="Custom", text_color=(0.5, 0.5, 0.5, 1),
                         size_hint_y=None, height=dp(20))
            T(l3, f"المتبقي: {u['remaining']:,.0f} دينار")
            c.add_widget(l3)
            box.add_widget(c)

    def back(self):
        self.manager.current = "home"


# ============================================================
# شاشة الإعدادات
# ============================================================
class SetScreen(Screen):
    def on_enter(self, *a):
        Clock.schedule_once(self._load, 0)

    def _load(self, dt):
        app = MDApp.get_running_app()
        db = app.db
        T(self.ids.st2, "الإعدادات")
        T(self.ids.sh2, "تعديل أسماء الإخوة")
        T(self.ids.bs, "حفظ الأسماء")
        T(self.ids.pw_title, "كلمة السر")
        T(self.ids.pw_btn, "تعيين كلمة سر جديدة")
        T(self.ids.pw_rm, "إزالة كلمة السر")
        T(self.ids.br, "إعادة تعيين جميع البيانات")
        for i in range(1, 6):
            self.ids[f"s{i}"].text = db.name(i)

    def save(self):
        app = MDApp.get_running_app()
        for i in range(1, 6):
            n = self.ids[f"s{i}"].text.strip()
            if n:
                app.db.set_name(i, n)
        Snackbar(text=AR("تم حفظ الأسماء")).open()

    def set_pw(self):
        pw = self.ids.pw_field.text.strip()
        if not pw:
            Snackbar(text=AR("أدخل كلمة السر")).open()
            return
        app = MDApp.get_running_app()
        app.db.set_password(pw)
        self.ids.pw_field.text = ""
        Snackbar(text=AR("تم تعيين كلمة السر")).open()

    def remove_pw(self):
        app = MDApp.get_running_app()
        app.db.remove_password()
        Snackbar(text=AR("تم إزالة كلمة السر")).open()

    def ask_reset(self):
        box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(50))
        l = MDLabel(halign="center", theme_text_color="Custom",
                    text_color=(0.78, 0.18, 0.18, 1))
        T(l, "سيتم حذف جميع الدفعات")
        box.add_widget(l)
        self._d = MDDialog(
            title=AR("تأكيد إعادة التعيين"), type="custom", content_cls=box,
            buttons=[
                MDFlatButton(text=AR("إلغاء"), on_release=lambda x: self._d.dismiss()),
                MDRaisedButton(text=AR("حذف الكل"), md_bg_color=(0.75, 0.18, 0.18, 1),
                               on_release=lambda x: self._reset()),
            ])
        self._d.open()

    def _reset(self):
        app = MDApp.get_running_app()
        app.db.reset()
        self._d.dismiss()
        self._load(None)

    def back(self):
        self.manager.current = "home"


# ============================================================
# التطبيق الرئيسي
# ============================================================
class LandApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.theme_style = "Light"
        self.title = "أرض الإخوة"
        self.db = DB()
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(DetailScreen(name="detail"))
        sm.add_widget(AddScreen(name="add"))
        sm.add_widget(SumScreen(name="summary"))
        sm.add_widget(AlertScreen(name="alerts"))
        sm.add_widget(SetScreen(name="settings"))
        return sm


if __name__ == "__main__":
    LandApp().run()