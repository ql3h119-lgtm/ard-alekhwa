# -*- coding: utf-8 -*-
import os, json, hashlib
from datetime import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

# إعدادات عامة
Window.clearcolor = (0.96, 0.96, 0.98, 1)
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arabic.ttf")
if os.path.exists(FONT_PATH):
    LabelBase.register(name="Arabic", fn_regular=FONT_PATH)

# محرك تشكيل اللغة العربية (مدمج لضمان عمل الـ APK)
ARABIC_MAP = {'أ': ('\ufe83', '\ufe83', '\ufe84', '\ufe84'), 'ب': ('\ufe89', '\ufe8b', '\ufe8c', '\ufe8a'), 'ت': ('\ufe95', '\ufe97', '\ufe98', '\ufe96'), 'ث': ('\ufe99', '\ufe9b', '\ufe9c', '\ufe9a'), 'ج': ('\ufe9d', '\ufe9f', '\ufea0', '\ufe9e'), 'ح': ('\ufea1', '\ufea3', '\ufea4', '\ufea2'), 'خ': ('\ufea5', '\ufea7', '\ufea8', '\ufea6'), 'د': ('\ufea9', '\ufea9', '\ufeaa', '\ufeaa'), 'ذ': ('\ufeab', '\ufeab', '\ufeac', '\ufeac'), 'ر': ('\ufead', '\ufead', '\ufeae', '\ufeae'), 'ز': ('\ufeaf', '\ufeaf', '\ufeb0', '\ufeb0'), 'س': ('\ufeb1', '\ufeb3', '\ufeb4', '\ufeb2'), 'ش': ('\ufeb5', '\ufeb7', '\ufeb8', '\ufeb6'), 'ص': ('\ufeb9', '\ufebb', '\ufebc', '\ufeba'), 'ض': ('\ufebd', '\ufebf', '\ufec0', '\ufebe'), 'ط': ('\ufec1', '\ufec3', '\ufec4', '\ufec2'), 'ظ': ('\ufec5', '\ufec7', '\ufec8', '\ufec6'), 'ع': ('\ufec9', '\ufecb', '\ufecc', '\ufeca'), 'غ': ('\ufecd', '\ufecf', '\uffed', '\ufece'), 'ف': ('\ufed1', '\ufed3', '\ufed4', '\ufed2'), 'ق': ('\ufed5', '\ufed7', '\ufed8', '\ufed6'), 'ك': ('\ufed9', '\ufedb', '\ufedc', '\ufeda'), 'ل': ('\ufedd', '\ufedf', '\ufee0', '\ufede'), 'م': ('\ufee1', '\ufee3', '\ufee4', '\ufee2'), 'ن': ('\ufee5', '\ufee7', '\ufee8', '\ufee6'), 'ه': ('\ufee9', '\ufeeb', '\ufeec', '\ufeea'), 'و': ('\ufeed', '\ufeed', '\ufeee', '\ufeee'), 'ي': ('\ufeef', '\ufef3', '\ufef4', '\ufef0'), 'ى': ('\ufeee', '\ufeee', '\ufef0', '\ufef0'), 'ة': ('\ufe93', '\ufe93', '\ufe94', '\ufe94'), 'لا': ('\ufefb', '\ufefb', '\ufefc', '\ufefc')}
RIGHT_ONLY = set('أادذرزوىة')

def AR(text):
    if not text: return ""
    s = str(text)
    reshaped = []
    words = s.split(' ')
    for word in words:
        chars = list(word)
        n = len(chars)
        new_word = []
        for i, ch in enumerate(chars):
            if ch not in ARABIC_MAP:
                new_word.append(ch)
                continue
            p_conn = (i > 0 and chars[i-1] in ARABIC_MAP and chars[i-1] not in RIGHT_ONLY)
            n_conn = (i < n - 1 and chars[i+1] in ARABIC_MAP)
            iso, init, med, fin = ARABIC_MAP[ch]
            if p_conn and n_conn: new_word.append(med)
            elif p_conn: new_word.append(fin)
            elif n_conn: new_word.append(init)
            else: new_word.append(iso)
        reshaped.append("".join(new_word[::-1]))
    return " ".join(reshaped[::-1])

# قاعدة البيانات
class DB:
    FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
    @classmethod
    def load(cls):
        if not os.path.exists(cls.FILE):
            d = {"pw": "", "bros": {str(i): {"n": f"الأخ {i}", "ps": []} for i in range(1, 6)}}
            cls.save(d); return d
        with open(cls.FILE, "r", encoding="utf-8") as f: return json.load(f)
    @classmethod
    def save(cls, data):
        with open(cls.FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)

class ARLabel(Label):
    def __init__(self, **kw):
        kw['font_name'] = 'Arabic'
        if 'text' in kw: kw['text'] = AR(kw['text'])
        super().__init__(**kw)

class ARButton(Button):
    def __init__(self, **kw):
        kw['font_name'] = 'Arabic'
        if 'text' in kw: kw['text'] = AR(kw['text'])
        super().__init__(**kw)

class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        l = BoxLayout(orientation='vertical', padding=40, spacing=20)
        l.add_widget(ARLabel(text="أرض الإخوة", font_size='35sp', bold=True, color=(0.1, 0.4, 0.8, 1)))
        self.ti = TextInput(password=True, multiline=False, size_hint_y=None, height=50)
        l.add_widget(self.ti)
        b = ARButton(text="دخول", size_hint_y=None, height=50, background_color=(0.1, 0.5, 0.9, 1))
        b.bind(on_release=self.go)
        l.add_widget(b)
        l.add_widget(ARLabel(text="بواسطة أبو جبر", font_size='12sp', color=(0.5, 0.5, 0.5, 1)))
        self.add_widget(l)
    def go(self, i):
        d = DB.load()
        p = self.ti.text.strip()
        h = hashlib.sha256(p.encode()).hexdigest() if p else ""
        if not d['pw'] or d['pw'] == h:
            if not d['pw'] and p: d['pw'] = h; DB.save(d)
            self.manager.current = 'home'

class HomeScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        d = DB.load()
        l = BoxLayout(orientation='vertical', padding=10, spacing=10)
        l.add_widget(ARLabel(text="المساحة: 2506 م² | السعر: 35,000 JOD", font_size='16sp', color=(0,0,0,1)))
        sv = ScrollView()
        g = GridLayout(cols=1, spacing=10, size_hint_y=None); g.bind(minimum_height=g.setter('height'))
        for i in range(1, 6):
            b_d = d['bros'][str(i)]
            paid = sum(p['a'] for p in b_d['ps'])
            c = BoxLayout(orientation='vertical', size_hint_y=None, height=80, padding=5)
            c.add_widget(ARLabel(text=f"{b_d['n']} | المدفوع: {paid}", color=(0,0,0,1)))
            btn = ARButton(text="التفاصيل", size_hint_y=None, height=35)
            btn.bind(on_release=lambda x, idx=i: self.det(idx))
            c.add_widget(btn)
            g.add_widget(c)
        sv.add_widget(g); l.add_widget(sv)
        self.add_widget(l)
    def det(self, idx):
        self.manager.get_screen('det').idx = idx
        self.manager.current = 'det'

class DetScreen(Screen):
    idx = 1
    def on_enter(self):
        self.clear_widgets()
        d = DB.load(); b_d = d['bros'][str(self.idx)]
        l = BoxLayout(orientation='vertical', padding=10, spacing=10)
        l.add_widget(ARLabel(text=f"اسم الأخ: {b_d['n']}", color=(0,0,0,1)))
        # إضافة دفعة
        self.ai = TextInput(hint_text="المبلغ", input_filter='int', size_hint_y=None, height=40)
        l.add_widget(self.ai)
        b = ARButton(text="إضافة دفعة 1000", size_hint_y=None, height=40)
        b.bind(on_release=self.add_p)
        l.add_widget(b)
        bb = ARButton(text="رجوع", size_hint_y=None, height=40)
        bb.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        l.add_widget(bb)
        self.add_widget(l)
    def add_p(self, i):
        d = DB.load()
        amt = int(self.ai.text) if self.ai.text else 1000
        d['bros'][str(self.idx)]['ps'].append({'a': amt, 'd': str(datetime.now().date())})
        DB.save(d); self.on_enter()

class LandApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(DetScreen(name='det'))
        return sm

if __name__ == '__main__':
    LandApp().run()
