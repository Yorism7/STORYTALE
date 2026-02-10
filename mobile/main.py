"""
StoryTale Kivy app – AI children's stories
รองรับ iOS และ Android (build กับ Buildozer / KiviOS)
"""
import os
import json
from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.network.urlrequest import UrlRequest
from kivy.core.audio import SoundLoader
import tempfile

# Backend base URL – เปลี่ยนเป็น IP จริงเมื่อรันบนมือถือ
API_BASE = os.environ.get("STORYTELL_API_BASE", "http://localhost:8000")

# ค่าที่ส่งไป API (ให้ตรงกับเว็บ)
STORY_LANG_VALUES = ["ไทย", "English"]
STORY_LANG_MAP = {"ไทย": "th", "English": "en"}
IMAGE_MODEL_VALUES = ["Flux Schnell", "Z-Image Turbo"]
IMAGE_MODEL_MAP = {"Flux Schnell": "flux", "Z-Image Turbo": "zimage"}
IMAGE_STYLE_LABELS = [
    "— เลือก —",
    "การ์ตูน",
    "วาดน้ำ",
    "เรโทร",
    "สามมิติ (3D)",
    "น่ารักคาวาอิ",
    "ภาพนิทาน",
    "พาสเทลนุ่ม",
    "สไตล์ดิสนีย์/พิกซาร์",
    "ปั้นดินน้ำมัน",
    "การ์ตูนสีสัน",
]
IMAGE_STYLE_VALUES = [
    "",
    "cartoon style",
    "watercolor painting",
    "retro vintage",
    "3d render, cute and child-friendly",
    "cute kawaii style, child-friendly",
    "children's storybook illustration",
    "soft pastel illustration, gentle colors",
    "disney pixar style, family-friendly",
    "claymation style, soft 3d",
    "colorful cartoon, bright and friendly",
]


Builder.load_string("""
#:set primary_color 0.91, 0.71, 0.72, 1
#:set secondary_color 0.66, 0.84, 0.73, 1
#:set surface_color 1, 0.96, 0.96, 1
#:set text_color 0.18, 0.20, 0.21, 1

<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        canvas.before:
            Color:
                rgba: surface_color
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'StoryTale'
            font_size: '28sp'
            bold: True
            color: text_color
            size_hint_y: None
            height: 50
        Label:
            text: 'นิทานเด็กจาก AI'
            font_size: '16sp'
            color: text_color
            opacity: 0.8
            size_hint_y: None
            height: 30
        TextInput:
            id: topic
            hint_text: 'หัวข้อหรือแนวเรื่อง (เช่น กระต่ายกับเต่า)'
            multiline: False
            size_hint_y: None
            height: 50
            padding: 15, 15
            font_size: '16sp'
            background_color: 1, 1, 1, 0.6
        Label:
            text: 'ภาษาของเรื่อง'
            font_size: '14sp'
            color: text_color
            size_hint_y: None
            height: 28
        Spinner:
            id: story_lang
            text: 'ไทย'
            values: ['ไทย', 'English']
            size_hint_y: None
            height: 44
        Label:
            text: 'โมเดลภาพ'
            font_size: '14sp'
            color: text_color
            size_hint_y: None
            height: 28
        Spinner:
            id: image_model
            text: 'Flux Schnell'
            values: ['Flux Schnell', 'Z-Image Turbo']
            size_hint_y: None
            height: 44
        Label:
            text: 'สไตล์ภาพ (ไม่บังคับ)'
            font_size: '14sp'
            color: text_color
            size_hint_y: None
            height: 28
        Spinner:
            id: image_style
            text: '— เลือก —'
            values: ['— เลือก —', 'การ์ตูน', 'วาดน้ำ', 'เรโทร', 'สามมิติ (3D)', 'น่ารักคาวาอิ', 'ภาพนิทาน', 'พาสเทลนุ่ม', 'สไตล์ดิสนีย์/พิกซาร์', 'ปั้นดินน้ำมัน', 'การ์ตูนสีสัน']
            size_hint_y: None
            height: 44
        Label:
            text: 'จำนวนตอน (1-10)'
            font_size: '14sp'
            color: text_color
            size_hint_y: None
            height: 30
        TextInput:
            id: num_ep
            input_filter: 'int'
            text: '5'
            multiline: False
            size_hint_y: None
            height: 45
            padding: 15, 15
            font_size: '16sp'
            background_color: 1, 1, 1, 0.6
        Button:
            id: btn_generate
            text: 'สร้างเรื่อง'
            font_size: '18sp'
            size_hint_y: None
            height: 56
            background_color: primary_color
            on_press: root.on_generate()
        Label:
            id: status
            text: ''
            font_size: '14sp'
            color: 0.6, 0.2, 0.2, 1
            size_hint_y: None
            height: 30
        Button:
            text: 'รายการเรื่องที่เก็บไว้'
            font_size: '16sp'
            size_hint_y: None
            height: 48
            background_color: secondary_color
            on_press: root.manager.current = 'list'

<StoryListScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        canvas.before:
            Color:
                rgba: surface_color
            Rectangle:
                pos: self.pos
                size: self.size
        Button:
            text: 'กลับ'
            size_hint_y: None
            height: 44
            background_color: primary_color
            on_press: root.manager.current = 'home'
        ScrollView:
            id: scroll
            do_scroll_x: False
            BoxLayout:
                id: list_container
                orientation: 'vertical'
                size_hint_y: None
                spacing: 10
                padding: 10

<StoryViewScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 15
        canvas.before:
            Color:
                rgba: surface_color
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: 44
            Button:
                text: 'กลับ'
                size_hint_x: None
                width: 100
                background_color: primary_color
                on_press: root.manager.current = 'home'
            Label:
                text: root.title or 'เรื่อง'
                font_size: '18sp'
                bold: True
                color: text_color
                halign: 'center'
                valign: 'middle'
            Label:
                text: root.page_indicator
                font_size: '14sp'
                color: text_color
                size_hint_x: None
                width: 60
        BoxLayout:
            orientation: 'vertical'
            spacing: 10
            AsyncImage:
                id: episode_image
                allow_stretch: True
                keep_ratio: True
                size_hint_y: None
                height: 220
            ScrollView:
                do_scroll_x: False
                Label:
                    id: episode_text
                    text: ''
                    font_size: '18sp'
                    color: text_color
                    size_hint_y: None
                    text_size: self.width, None
        Button:
            text: 'เล่นเสียงอ่าน'
            size_hint_y: None
            height: 44
            background_color: secondary_color
            on_press: root.play_tts()
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 20
            Button:
                text: 'ก่อนหน้า'
                background_color: primary_color
                on_press: root.prev_page()
            Button:
                text: 'ถัดไป'
                background_color: primary_color
                on_press: root.next_page()
""")


class HomeScreen(Screen):
    def on_generate(self):
        topic = self.ids.topic.text.strip()
        if not topic:
            self.ids.status.text = "กรุณาใส่หัวข้อ"
            return
        try:
            num = int(self.ids.num_ep.text or "5")
            num = max(1, min(10, num))
        except ValueError:
            num = 5
        story_lang = STORY_LANG_MAP.get(self.ids.story_lang.text, "th")
        image_model = IMAGE_MODEL_MAP.get(self.ids.image_model.text, "flux")
        style_text = self.ids.image_style.text
        image_style = None
        if style_text and style_text != "— เลือก —":
            idx = IMAGE_STYLE_LABELS.index(style_text) if style_text in IMAGE_STYLE_LABELS else -1
            if idx >= 0 and idx < len(IMAGE_STYLE_VALUES):
                image_style = IMAGE_STYLE_VALUES[idx] or None
        self.ids.status.text = "กำลังสร้างเรื่อง..."
        self.ids.btn_generate.disabled = True
        payload = {
            "topic": topic,
            "num_episodes": num,
            "story_lang": story_lang,
            "image_model": image_model,
        }
        if image_style:
            payload["image_style"] = image_style
        body = json.dumps(payload)
        url = f"{API_BASE}/api/story/generate"
        req = UrlRequest(
            url,
            req_body=body,
            req_headers={"Content-Type": "application/json"},
            on_success=self._on_success,
            on_failure=self._on_failure,
            on_error=self._on_error,
        )

    @mainthread
    def _on_success(self, req, result):
        self.ids.btn_generate.disabled = False
        self.ids.status.text = ""
        story_id = result.get("storyId")
        if story_id:
            sm = self.manager
            sm.get_screen("view").load_story(result)
            sm.current = "view"
        else:
            self.ids.status.text = "ตอบกลับไม่ถูกต้อง"

    @mainthread
    def _on_failure(self, req, result):
        self.ids.btn_generate.disabled = False
        if isinstance(result, dict) and result.get("detail"):
            detail = result["detail"]
            self.ids.status.text = detail if isinstance(detail, str) else str(detail)
        else:
            self.ids.status.text = "สร้างไม่สำเร็จ (เช็ค backend หรือเครือข่าย)"

    @mainthread
    def _on_error(self, req, error):
        self.ids.btn_generate.disabled = False
        self.ids.status.text = "เกิดข้อผิดพลาด (เช็คเครือข่าย)"


class StoryListScreen(Screen):
    def on_enter(self, *args):
        super().on_enter(*args)
        self._load_list()

    def _load_list(self):
        container = self.ids.list_container
        container.clear_widgets()
        url = f"{API_BASE}/api/stories"
        UrlRequest(
            url,
            on_success=self._on_list_success,
            on_failure=lambda req, res: None,
            on_error=lambda req, err: None,
        )

    def _format_date(self, iso_str):
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return dt.strftime("%d/%m/%y")
        except Exception:
            return iso_str[:10] if iso_str else ""

    @mainthread
    def _on_list_success(self, req, result):
        container = self.ids.list_container
        container.clear_widgets()
        if not result:
            container.add_widget(Label(text="ยังไม่มีเรื่องที่เก็บไว้", font_size="16sp"))
            return
        for s in result:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=72, spacing=8, padding=(8, 4))
            thumb_url = s.get("first_episode_image_url") or ""
            if thumb_url:
                img = AsyncImage(
                    source=thumb_url,
                    size_hint_x=None,
                    width=56,
                    allow_stretch=True,
                    keep_ratio=True,
                )
                row.add_widget(img)
            title = s.get("title", "") or "ไม่มีชื่อ"
            meta = f"{s.get('num_episodes', 0)} ตอน · {self._format_date(s.get('created_at', ''))}"
            btn = Button(
                text=f"{title}\n{meta}",
                font_size="15sp",
                size_hint_y=None,
                height=72,
                background_color=(0.9, 0.9, 0.95, 1),
            )
            sid = s.get("storyId", "")
            btn.bind(on_press=lambda __, story_id=sid: self._open_story(story_id))
            row.add_widget(btn)
            container.add_widget(row)
        container.height = len(result) * 72 + max(0, len(result) - 1) * 10

    def _open_story(self, story_id):
        url = f"{API_BASE}/api/story/{story_id}"
        def on_ok(req, result):
            self.manager.get_screen("view").load_story(result)
            self.manager.current = "view"
        UrlRequest(url, on_success=on_ok)


class StoryViewScreen(Screen):
    title = StringProperty("")
    page_indicator = StringProperty("1/1")
    _data = ObjectProperty(None, allownone=True)
    _index = NumericProperty(0)

    def load_story(self, data):
        self._data = data
        self._index = 0
        self.title = data.get("title", "")
        self._update_page()

    def _update_page(self):
        if not self._data:
            return
        eps = self._data.get("episodes", [])
        n = len(eps)
        self.page_indicator = f"{self._index + 1}/{n}"
        if self._index < n:
            ep = eps[self._index]
            self.ids.episode_text.text = ep.get("text", "")
            url = ep.get("imageUrl", "")
            self.ids.episode_image.source = url if url else ""

    def next_page(self):
        if not self._data:
            return
        n = len(self._data.get("episodes", []))
        if self._index < n - 1:
            self._index += 1
            self._update_page()

    def prev_page(self):
        if self._index > 0:
            self._index -= 1
            self._update_page()

    def play_tts(self):
        if not self._data:
            return
        eps = self._data.get("episodes", [])
        if self._index >= len(eps):
            return
        story_id = self._data.get("storyId", "")
        url = f"{API_BASE}/api/story/{story_id}/episode/{self._index}/audio"
        def on_success(req, result):
            try:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    f.write(result)
                    path = f.name
                sound = SoundLoader.load(path)
                if sound:
                    sound.play()
            except Exception as e:
                print(f"[StoryTale] TTS play error: {e}")
        UrlRequest(url, on_success=on_success)


class StoryTaleApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(StoryListScreen(name="list"))
        sm.add_widget(StoryViewScreen(name="view"))
        return sm


if __name__ == "__main__":
    StoryTaleApp().run()
