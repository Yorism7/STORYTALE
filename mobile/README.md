# StoryTale Mobile (Kivy)

Python/Kivy app for iOS and Android – same codebase.

## Run on PC

```bash
cd mobile
pip install -r requirements.txt
# Point to your backend IP (use real IP if testing on device)
set STORYTELL_API_BASE=http://192.168.x.x:8000   # Windows
export STORYTELL_API_BASE=http://192.168.x.x:8000   # macOS/Linux
python main.py
```

## Build for devices

- **Android:** Buildozer (see Kivy docs)
- **iOS:** KiviOS / python-for-android (build on macOS)
