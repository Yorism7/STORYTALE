# ส่ง App ขึ้น Official Showcase ของ pollinations.ai

## สิ่งที่ต้องกรอกในฟอร์ม (Submit Your App)

| ช่อง | สิ่งที่กรอก | หมายเหตุ |
|------|-------------|----------|
| **App Name** * | `StoryTale` | ชื่อแอปตาม README |
| **App Description** * | ดูตัวอย่างด้านล่าง | อธิบายว่าแอปทำอะไร และใช้ pollinations.ai อย่างไร |
| **App URL** * | URL แอปที่ deploy แล้ว เช่น `https://your-app.onrender.com` หรือ `https://storytale.vercel.app` | ต้องเป็น URL ที่เข้าถึงได้จริง |
| **GitHub Open Source Repository URL** | `https://github.com/<YOUR_GITHUB_USERNAME>/STORYTELL` | แทนที่ `<YOUR_GITHUB_USERNAME>` ด้วย username จริง |
| **Discord Username** | (ถ้ามี) | ไม่บังคับ |
| **App Language** | `th` หรือ `en, th` | แอปรองรับไทยและอังกฤษ |
| **Email / Other Contact** * | อีเมล หรือ Twitter/เว็บไซต์ | ใช้สำหรับให้ทีม pollinations ติดต่อ |

### ตัวอย่าง App Description (Markdown)

```markdown
**StoryTale** is an AI-powered app for children's stories. Users enter a topic (e.g. "rabbit and turtle") and get a short story with multiple episodes, each with an AI-generated illustration. The app also supports read-aloud (Edge TTS) and MP4 video export.

**How it uses pollinations.ai:**
- **Story text:** We use the pollinations.ai Chat Completions API (gemini-fast) to generate story structure and episode text in JSON (title, episodes with text and image prompts, character description, art style).
- **Images:** We use the pollinations.ai Image API (Flux / Z-Image) to generate consistent, child-friendly illustrations for each episode. Prompts include character consistency and art style from the story JSON.

The backend is FastAPI; the frontend is React (Vite). API key is configured via `POLLINATIONS_API_KEY` (from enter.pollinations.ai).
```

---

## สิ่งที่เพิ่มในระบบแล้ว (ในโปรเจกต์นี้)

1. **Frontend (เว็บ)**  
   - **Footer ทุกหน้า:** ลิงก์ "Built with pollinations.ai" / "สร้างด้วย pollinations.ai" ไปที่ https://pollinations.ai  
   - ไฟล์: `web/src/App.tsx` (คอมโพเนนต์ `SiteFooter`), `web/src/context/LangContext.tsx` (คำแปล `poweredBy`)

2. **README**  
   - แบดจ์ "Built with pollinations.ai" ด้านบน (ลิงก์ไป https://pollinations.ai)  
   - บรรทัดอธิบายว่า Story และภาพใช้ [pollinations.ai](https://pollinations.ai) API  
   - ไฟล์: `README.md`

3. **ข้อกำหนดที่ครบแล้ว**  
   - มีบัญชีที่ enter.pollinations.ai (ต้องสมัครด้วย GitHub เอง)  
   - แอปใช้ pollinations.ai API (Chat Completions + Image) — ใช้อยู่แล้วใน `backend/app/services/pollinations.py`  
   - เครดิตใน frontend และลิงก์ใน README — เพิ่มแล้วตามด้านบน  

4. **โลโก้/แบดจ์อย่างเป็นทางการ (ถ้าต้องการ)**  
   - ฟอร์มระบุ: Official logos (Logo White / Logo Text White), Official Badge: Built With pollinations.ai  
   - ถ้า pollinations แจ้ง URL ของรูปแบดจ์/โลโก้อย่างเป็นทางการ สามารถนำมาใส่ใน README หรือใน footer ของเว็บแทนของปัจจุบันได้

---

## Checklist ก่อนส่ง

- [ ] สมัคร/ล็อกอินที่ [enter.pollinations.ai](https://enter.pollinations.ai) ด้วย GitHub
- [ ] Deploy แอปให้มี URL สาธารณะ (เช่น Render, Vercel) แล้วใส่ในช่อง App URL
- [ ] กรอก App Name, Description, App URL, GitHub repo URL, Contact
- [ ] ใส่ App Language: `th` (หรือ `en, th`)
- [ ] ตรวจว่า footer ในเว็บแสดง "Built with pollinations.ai" และ README มีลิงก์ไป pollinations.ai
