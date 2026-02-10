# StoryTale Mobile (Kivy)

แอป Kivy สำหรับ Android (และ iOS ถ้า build บน Mac) ใช้ API ตัวเดียวกับเว็บ

---

## รันบน PC

```bash
cd mobile
pip install -r requirements.txt
# ชี้ไปที่ backend (ใช้ IP จริงถ้าทดบนมือถือ)
set STORYTELL_API_BASE=http://192.168.x.x:8000   # Windows
export STORYTELL_API_BASE=http://192.168.x.x:8000   # macOS/Linux
python main.py
```

---

## Build เป็น APK (Android) ด้วย Buildozer

### 1. ติดตั้ง Buildozer และเครื่องมือ (Linux หรือ WSL2 แนะนำ)

**Ubuntu / Debian:**

Buildozer ใช้ `pip install --user` ข้างใน จึงไม่เหมาะกับ pipx/venv ควรติดตั้งกับ system Python:

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev python3-setuptools
# ติดตั้ง buildozer + cython (--break-system-packages จำเป็นบน Ubuntu 24.04+ เพราะระบบห้าม pip ลง system)
pip install --break-system-packages buildozer cython
```

ถ้าต้องการใช้ pipx (ต้อง inject dependencies และยอมเสี่ยงว่า build อาจพัง): `pipx install buildozer` แล้ว `pipx inject buildozer setuptools appdirs colorama jinja2 "sh" build toml packaging` แต่ถ้า buildozer ยังรัน `pip install --user` อยู่จะ error — แนะนำใช้วิธีด้านบน

**macOS:**
```bash
brew install autoconf automake libtool pkg-config
brew install openjdk
pip install buildozer cython
```

**Windows:** ใช้ WSL2 (Ubuntu) แล้วทำตามขั้นตอน Ubuntu ด้านบน จะ build ได้เสถียรที่สุด

### 2. ลง Android SDK (ถ้า Buildozer ยังไม่ดึงอัตโนมัติ)

Buildozer จะดาวน์โหลด SDK/NDK เองครั้งแรกที่ build ถ้าไม่มีอยู่แล้ว (ใช้เวลาครั้งแรกนาน)

### 3. Build APK

บน Ubuntu 24.04+ (Python 3.11+) ต้องให้ pip ที่ buildozer เรียกข้าม "externally-managed-environment":

```bash
cd mobile
PIP_BREAK_SYSTEM_PACKAGES=1 buildozer android debug
```

ผลลัพธ์ APK อยู่ที่: `mobile/bin/StoryTale-0.1.0-arm64-v8a-debug.apk` (หรือชื่อใกล้เคียง)

### 4. Build release (ลงร้าน Play ได้)

```bash
buildozer android release
```

ก่อน build release ควรแก้ `buildozer.spec`:
- ใส่ `android.release_artifact = apk` (หรือ aab ถ้าต้องส่ง Play Store)
- ตั้งค่า keystore ถ้าต้อง signing (ดูใน [Buildozer docs](https://buildozer.readthedocs.io/))

### คำสั่งอื่นที่ใช้บ่อย

| คำสั่ง | ความหมาย |
|--------|-----------|
| `buildozer android debug` | Build APK แบบ debug ไว้ติดตั้งทดสอบ |
| `buildozer android clean` | ล้าง build ก่อน build ใหม่ |
| `buildozer android debug 2>&1 \| tee build.log` | Build แล้วเก็บ log ไว้ใน build.log |

### หมายเหตุ

- **ครั้งแรก** build อาจใช้เวลา 20–40 นาที (โหลด SDK, NDK, compile)
- แนะนำให้ใช้ **Linux หรือ WSL2** จะ build ได้ครบถ้วน; บน Windows โดยตรงอาจมีปัญหา
- ตั้ง **API Base** ให้ชี้ไปที่ backend จริง (เช่น เซิร์ฟเวอร์ที่ deploy ไว้ หรือ IP ในเครือข่ายเดียวกัน) ผ่าน env `STORYTELL_API_BASE` หรือแก้ในแอปก่อน build
- ใน `buildozer.spec` ใช้ **Python 3.10.x** (เช่น `python3==3.10.18,hostpython3==3.10.18`) เพื่อหลีก error จาก pyjnius กับ Python 3.12 และเพราะ python.org ไม่มี `Python-3.10.tgz` แล้ว (ต้องระบุเวอร์ชันเต็ม เช่น 3.10.18)
- โปรเจกต์ใช้ **local recipe** `recipes/pyjnius` พร้อม patch **py3_long_fix.patch** เพื่อให้ pyjnius compile กับ host Python 3.12 ได้ (ใน Python 3 ไม่มี `long` แล้ว ใช้ `int` แทน) — ตั้ง `p4a.local_recipes = recipes` ใน spec (path เทียบกับโฟลเดอร์ที่รัน buildozer). ถ้า build ยัง error เรื่อง `long` ให้ลองใช้ **path แบบ absolute** เช่น `p4a.local_recipes = /mnt/f/PROJECT_DEV/STORYTELL/mobile/recipes` (บน WSL)
- ถ้าเคย build ด้วย Python 3.11/3.12 มาก่อน ต้อง **ล้าง build แล้วรันใหม่**: `buildozer android clean` แล้วค่อย `PIP_BREAK_SYSTEM_PACKAGES=1 buildozer android debug`

---

## iOS (ถ้ามี Mac)

ใช้ KiviOS หรือ python-for-ios (ต้อง build บน macOS กับ Xcode) ดูที่ [Kivy iOS](https://kivy.org/doc/stable/guide/packaging-ios.html)
