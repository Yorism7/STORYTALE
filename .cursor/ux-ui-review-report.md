# UX/UI Review Report – StoryTale Web

**ขอบเขต:** หน้าหลัก (Home), รายการเรื่อง (StoryList), หน้ามองเรื่อง (StoryView), LangSwitcher, โครงสร้างแอป  
**วันที่:** 2026-02-06  
**สถานะ:** แก้ไขตามคำแนะนำทั้งหมดแล้ว (2026-02-06)

---

## Critical (ต้องแก้ – บล็อกการใช้งานหรือการเข้าถึง)

### 1. ป้ายกำกับฟอร์มไม่ผูกกับ input (Accessibility)
**ไฟล์:** `web/src/pages/Home.tsx`

ทุก `<label>` ไม่มี `htmlFor` และ input/select ไม่มี `id` ทำให้:
- คลิกที่ label ไม่โฟกัสไปที่ช่อง
- Screen reader อาจอ่านความสัมพันธ์ label–control ไม่ชัด

**แก้ไขตัวอย่าง:**
```tsx
<label htmlFor="topic" className="block text-sm font-medium text-text mb-2">
  {t('topicLabel')}
</label>
<input
  id="topic"
  type="text"
  ...
/>
```
ทำในทำนองเดียวกันกับทุกคู่ label + input/select (storyLang, imageModel, imageStyle, numEpisodes).

---

### 2. ลิงก์ "ดูรายการเรื่องที่เก็บไว้" ใช้ full page reload
**ไฟล์:** `web/src/pages/Home.tsx` (บรรทัด 139–144)

ใช้ `<a href="/stories">` แทน `<Link to="/stories">` ทำให้กดแล้วโหลดทั้งหน้า ไม่ใช่ SPA navigation (state หาย, ช้ากว่า)

**แก้ไข:** ใช้ `Link` จาก `react-router-dom` และ `to="/stories"` แทน `<a href="/stories">`.

---

### 3. ไม่แจ้งผู้ใช้เมื่อส่งออกวิดีโอล้มเหลว
**ไฟล์:** `web/src/pages/StoryView.tsx` (บรรทัด 149–165)

เมื่อ `exportVideo()` throw จะมีแค่ `console.error` ผู้ใช้ไม่เห็นข้อความ (มี key `exportVideoError` ใน LangContext แล้วแต่ไม่ได้ใช้)

**แก้ไข:** เก็บ error ใน state แล้วแสดงข้อความ `t('exportVideoError')` ใต้ปุ่มหรือใน role="alert".

---

## Should fix (ควรแก้ – มีผลต่อ UX/การมองเห็น)

### 4. ปุ่มสลับภาษา EN/TH ขนาดเล็ก (Touch target)
**ไฟล์:** `web/src/context/LangContext.tsx`

ปุ่มใช้ `px-2.5 py-1 text-sm` ขนาดต่ำกว่า ~44px ที่แนะนำสำหรับ touch

**แก้ไข:** เพิ่ม padding ให้ปุ่มใหญ่ขึ้น เช่น `px-4 py-2.5` หรือ `min-h-[44px] min-w-[44px]` สำหรับแต่ละปุ่ม

---

### 5. ใช้ `alert()` สำหรับ "คัดลอกลิงก์แล้ว"
**ไฟล์:** `web/src/pages/StoryView.tsx` (บรรทัด 71)

`alert()` บล็อก UI และไม่เหมาะกับ screen reader / โฟกัส

**แก้ไข:** ใช้ข้อความแจ้งชั่วคราว (toast/snackbar) หรือ `aria-live="polite"` + ข้อความใน div ที่อัปเดตหลังคัดลอก แล้วลบ/ซ่อนหลัง 2–3 วินาที

---

### 6. ภาษาในเอกสาร HTML ตายตัว
**ไฟล์:** `web/index.html`

`<html lang="th">` ตรึงเป็นไทย ทั้งที่แอปสลับ EN/TH ได้

**แก้ไข:** ตั้ง `lang` ตาม locale (เช่น ใน `main.tsx` หรือ root component อัปเดต `document.documentElement.lang` เมื่อ locale เปลี่ยน)

---

### 7. หัวข้อหน้ามองเรื่อง (StoryView) แคบบนมือถือ
**ไฟล์:** `web/src/pages/StoryView.tsx` (บรรทัด 78–80)

`truncate max-w-[60%]` บน header ที่มี 3 ส่วน (กลับ+แชร์ | ชื่อเรื่อง | 1/5) อาจทำให้ชื่อเรื่องเหลือพื้นที่น้อยบนจอเล็ก

**แก้ไข:** ลด max-width เป็น % ที่เล็กลงบน mobile หรือใช้ `sm:max-w-[60%]` และให้เต็มความกว้างบนจอเล็ก พร้อมตรวจ layout ว่าไม่ล้น

---

## Suggestions (ปรับปรุงเพิ่มเติม)

### 8. โฟกัสที่เห็นชัด (Focus visible)
ส่วนใหญ่ใช้ `focus:ring-2 focus:ring-primary` ดีอยู่แล้ว ควรตรวจให้ทุกปุ่ม/ลิงก์/input มี ring ชัด (โดยเฉพาะปุ่มใน footer ของ StoryView)

---

### 9. สถานะโหลดเสียง (Play audio)
**ไฟล์:** `web/src/pages/StoryView.tsx`

ปุ่ม "เล่นเสียงอ่าน" ไม่มีสถานะ loading ตอนโหลดไฟล์เสียง (ก่อนเล่น)

**แก้ไข:** ใส่ state เช่น `audioLoading` ระหว่าง request แล้วแสดงข้อความ "กำลังโหลด..." หรือ spinner ในปุ่ม

---

### 10. การตรวจสอบ Episodes (1–10)
**ไฟล์:** `web/src/pages/Home.tsx`

input ใช้ `value={numEpisodes}` และ `onChange` ที่ clamp อยู่แล้ว แต่ถ้าผู้ใช้พิมพ์ 0 หรือ 11 ไม่มีข้อความแจ้งว่าช่วงที่ใช้ได้คือ 1–10

**แก้ไข:** (ถ้าต้องการ) แสดงข้อความช่วยใต้ input เมื่อ value นอกช่วง เช่น "กรุณาเลือกระหว่าง 1–10"

---

### 11. Skip link
แอปไม่มี "Skip to main content" สำหรับผู้ใช้คีย์บอร์ด

**แก้ไข:** เพิ่มลิงก์ซ่อนที่โฟกัสได้ที่ด้านบน (เช่น `.sr-only` + `focus:not-sr-only`) นำไปยัง `<main>` เพื่อข้าม header

---

### 12. Motion / โปร่งใส
**ไฟล์:** `web/src/index.css`

มี `prefers-reduced-motion` อยู่แล้ว ดี  
การเปลี่ยนหน้า/สลับตอนไม่มี transition เล็กน้อย อาจเพิ่ม `transition-opacity` หรือ fade สั้นๆ ตอนสลับ episode (ถ้าต้องการให้รู้สึกนุ่มนวลขึ้น)

---

## สรุปจุดแข็ง

- โทนสีและพื้นหลังเหมาะกับแอปเด็ก (primary/surface)
- มี loading / error / disabled state ในฟอร์มและปุ่ม
- ใช้ semantic (heading, list, role="alert" ที่ error)
- LangSwitcher ใช้ `aria-pressed`
- รองรับ reduced motion ใน CSS
- Responsive: grid ใน StoryList, flex-col/flex-row ใน StoryView ตาม breakpoint
- รูปใน StoryView มี `alt` ที่อธิบายตอน

---

**สรุป:** แก้ Critical 3 จุด (label–input, Link แทน a, แจ้ง error ส่งออกวิดีโอ) ก่อน แล้วค่อยทำ Should fix และ Suggestions ตามลำดับความสำคัญของทีม
