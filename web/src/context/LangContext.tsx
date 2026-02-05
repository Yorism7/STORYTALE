import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'

export type Locale = 'en' | 'th'

const STORAGE_KEY = 'storytale-locale'

const translations: Record<Locale, Record<string, string>> = {
  en: {
    appTitle: 'StoryTale',
    appTagline: "AI children's stories – pick a topic, create a story with images",
    topicLabel: 'Topic or theme',
    topicPlaceholder: 'e.g. rabbit and turtle, lost bear cub',
    imageModelLabel: 'Image model',
    imageStyleLabel: 'Image style (optional)',
    selectOption: '— Select —',
    episodesLabel: 'Episodes (1–10)',
    createStory: 'Create story',
    creating: 'Creating story...',
    viewSavedStories: 'View saved stories',
    errorGeneric: 'Something went wrong',
    back: 'Back',
    storyListTitle: 'Saved stories',
    loading: 'Loading...',
    noStories: 'No saved stories yet. Create one from the home page.',
    episodesCount: 'episodes',
    storyNotFound: 'Story not found',
    loadFailed: 'Failed to load',
    backHome: 'Back to home',
    shareLink: 'Share link',
    linkCopied: 'Link copied',
    episodeAlt: 'Episode',
    noImage: 'No image',
    playAudio: 'Play audio',
    stopAudio: 'Stop audio',
    prev: 'Previous',
    next: 'Next',
    exportVideo: 'Export MP4 video',
    exporting: 'Exporting...',
    exportVideoError: 'Video export failed',
    storyLangLabel: 'Story language',
    storyLangEn: 'English',
    storyLangTh: 'ไทย',
  },
  th: {
    appTitle: 'StoryTale',
    appTagline: 'นิทานเด็กจาก AI – เลือกหัวข้อ แล้วสร้างเรื่องพร้อมภาพ',
    topicLabel: 'หัวข้อหรือแนวเรื่อง',
    topicPlaceholder: 'เช่น กระต่ายกับเต่า, ลูกหมีหลงทาง',
    imageModelLabel: 'โมเดลภาพ',
    imageStyleLabel: 'สไตล์ภาพ (ไม่บังคับ)',
    selectOption: '— เลือก —',
    episodesLabel: 'จำนวนตอน (1–10)',
    createStory: 'สร้างเรื่อง',
    creating: 'กำลังสร้างเรื่อง...',
    viewSavedStories: 'ดูรายการเรื่องที่เก็บไว้',
    errorGeneric: 'เกิดข้อผิดพลาด',
    back: 'กลับ',
    storyListTitle: 'รายการเรื่องที่เก็บไว้',
    loading: 'กำลังโหลด...',
    noStories: 'ยังไม่มีเรื่องที่เก็บไว้ สร้างเรื่องใหม่จากหน้าหลัก',
    episodesCount: 'ตอน',
    storyNotFound: 'ไม่พบเรื่อง',
    loadFailed: 'โหลดไม่สำเร็จ',
    backHome: 'กลับหน้าหลัก',
    shareLink: 'แชร์ลิงก์',
    linkCopied: 'คัดลอกลิงก์แล้ว',
    episodeAlt: 'ตอนที่',
    noImage: 'ไม่มีภาพ',
    playAudio: 'เล่นเสียงอ่าน',
    stopAudio: 'หยุดเสียง',
    prev: 'ก่อนหน้า',
    next: 'ถัดไป',
    exportVideo: 'ส่งออกวิดีโอ MP4',
    exporting: 'กำลังส่งออก...',
    exportVideoError: 'ส่งออกวิดีโอไม่สำเร็จ',
    storyLangLabel: 'ภาษาของเรื่อง',
    storyLangEn: 'English',
    storyLangTh: 'ไทย',
  },
}

type LangContextValue = {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: string) => string
}

const LangContext = createContext<LangContextValue | null>(null)

export function LangProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(() => {
    if (typeof window === 'undefined') return 'en'
    const stored = localStorage.getItem(STORAGE_KEY) as Locale | null
    return stored === 'en' || stored === 'th' ? stored : 'en'
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, locale)
  }, [locale])

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next)
  }, [])

  const t = useCallback(
    (key: string) => {
      return translations[locale][key] ?? key
    },
    [locale]
  )

  return (
    <LangContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LangContext.Provider>
  )
}

export function useLang() {
  const ctx = useContext(LangContext)
  if (!ctx) throw new Error('useLang must be used within LangProvider')
  return ctx
}

export function LangSwitcher() {
  const { locale, setLocale } = useLang()
  return (
    <div className="flex items-center gap-1 rounded-lg border border-primary/30 bg-white/60 p-0.5">
      <button
        type="button"
        onClick={() => setLocale('en')}
        className={`rounded-md px-2.5 py-1 text-sm font-medium transition-colors ${
          locale === 'en'
            ? 'bg-primary text-white'
            : 'text-text/70 hover:bg-primary/10 hover:text-text'
        }`}
        aria-pressed={locale === 'en'}
      >
        EN
      </button>
      <button
        type="button"
        onClick={() => setLocale('th')}
        className={`rounded-md px-2.5 py-1 text-sm font-medium transition-colors ${
          locale === 'th'
            ? 'bg-primary text-white'
            : 'text-text/70 hover:bg-primary/10 hover:text-text'
        }`}
        aria-pressed={locale === 'th'}
      >
        TH
      </button>
    </div>
  )
}
