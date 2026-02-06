import { useState, useRef, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useLang } from '../context/LangContext'
import { generateStory } from '../api/client'
import {
  IconBookOpen,
  IconTopic,
  IconLanguage,
  IconImage,
  IconEpisodes,
  IconLibrary,
} from '../components/icons/HomeIcons'

const IMAGE_STYLE_OPTIONS: { value: string; labelKey: string }[] = [
  { value: 'cartoon style', labelKey: 'imageStyleCartoon' },
  { value: 'watercolor painting', labelKey: 'imageStyleWatercolor' },
  { value: 'retro vintage', labelKey: 'imageStyleRetro' },
  { value: '3d render, cute and child-friendly', labelKey: 'imageStyle3d' },
  { value: 'cute kawaii style, child-friendly', labelKey: 'imageStyleKawaii' },
  { value: 'children\'s storybook illustration', labelKey: 'imageStyleStorybook' },
  { value: 'soft pastel illustration, gentle colors', labelKey: 'imageStylePastel' },
  { value: 'disney pixar style, family-friendly', labelKey: 'imageStyleDisney' },
  { value: 'claymation style, soft 3d', labelKey: 'imageStyleClay' },
  { value: 'colorful cartoon, bright and friendly', labelKey: 'imageStyleColorful' },
]

export default function Home() {
  const navigate = useNavigate()
  const { t } = useLang()
  const [topic, setTopic] = useState('')
  const [numEpisodes, setNumEpisodes] = useState(5)
  const [storyLang, setStoryLang] = useState<'en' | 'th'>('en')
  const [imageModel, setImageModel] = useState<'flux' | 'zimage'>('flux')
  const [imageStyle, setImageStyle] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const progressIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!loading) return
    setProgress(0)
    progressIntervalRef.current = setInterval(() => {
      setProgress((p) => {
        if (p >= 85) return p
        return p + Math.random() * 4 + 2
      })
    }, 800)
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
        progressIntervalRef.current = null
      }
    }
  }, [loading])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!topic.trim()) return
    setError('')
    setLoading(true)
    const clampedEpisodes = Math.min(10, Math.max(1, numEpisodes))
    try {
      const data = await generateStory({
        topic: topic.trim(),
        num_episodes: clampedEpisodes,
        story_lang: storyLang,
        image_model: imageModel,
        image_style: imageStyle || undefined,
      })
      navigate(`/story/${data.storyId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errorGeneric'))
      console.error('[StoryTale] generate error:', err)
    } finally {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
        progressIntervalRef.current = null
      }
      setProgress(100)
      setLoading(false)
      setTimeout(() => setProgress(0), 400)
    }
  }

  return (
    <div className="min-h-full flex flex-col items-center justify-center p-4 sm:p-6 bg-home-hero relative z-10">
      <header className="text-center mb-6 sm:mb-8 animate-fade-in-up">
        <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-white/90 shadow-lg shadow-primary/25 border border-primary/20 mb-4 animate-float text-primary">
          <IconBookOpen size={48} className="w-full h-full max-w-[3.5rem] max-h-[3.5rem] sm:max-w-[4.5rem] sm:max-h-[4.5rem]" />
        </div>
        <h1 className="text-3xl sm:text-5xl font-bold text-text mb-2 tracking-tight">
          {t('appTitle')}
        </h1>
        <p className="text-base sm:text-lg text-text/75 max-w-sm mx-auto leading-relaxed">
          {t('appTagline')}
        </p>
      </header>

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl bg-white/90 backdrop-blur-sm shadow-xl shadow-primary/20 p-6 sm:p-8 border border-primary/20 animate-fade-in-up"
        style={{ animationDelay: '0.1s' }}
      >
        <div className="space-y-4">
          <label htmlFor="topic" className="flex items-center gap-2 text-sm font-semibold text-text mb-2">
            <IconTopic className="text-primary shrink-0" size={18} />
            {t('topicLabel')}
          </label>
          <input
            id="topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder={t('topicPlaceholder')}
            className="w-full rounded-xl border-2 border-primary/30 bg-white px-4 py-3.5 text-text placeholder:text-text/45 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200"
            disabled={loading}
            maxLength={500}
            aria-invalid={!!error}
          />
        </div>

        <div className="mt-6 pt-6 border-t border-primary/15 space-y-4">
          <label htmlFor="storyLang" className="flex items-center gap-2 text-sm font-semibold text-text mb-2">
            <IconLanguage className="text-primary shrink-0" size={18} />
            {t('storyLangLabel')}
          </label>
          <select
            id="storyLang"
            value={storyLang}
            onChange={(e) => setStoryLang(e.target.value as 'en' | 'th')}
            className="w-full rounded-xl border-2 border-primary/30 bg-white px-4 py-3 text-text focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200 cursor-pointer"
            disabled={loading}
          >
            <option value="en">{t('storyLangEn')}</option>
            <option value="th">{t('storyLangTh')}</option>
          </select>

          <label htmlFor="imageModel" className="flex items-center gap-2 text-sm font-semibold text-text mt-4 mb-2">
            <IconImage className="text-primary shrink-0" size={18} />
            {t('imageModelLabel')}
          </label>
          <select
            id="imageModel"
            value={imageModel}
            onChange={(e) => setImageModel(e.target.value as 'flux' | 'zimage')}
            className="w-full rounded-xl border-2 border-primary/30 bg-white px-4 py-3 text-text focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200 cursor-pointer"
            disabled={loading}
          >
            <option value="flux">Flux Schnell</option>
            <option value="zimage">Z-Image Turbo</option>
          </select>

          <label htmlFor="imageStyle" className="flex items-center gap-2 text-sm font-semibold text-text mt-4 mb-2">
            <IconImage className="text-primary shrink-0" size={18} />
            {t('imageStyleLabel')}
          </label>
          <select
            id="imageStyle"
            value={imageStyle}
            onChange={(e) => setImageStyle(e.target.value)}
            className="w-full rounded-xl border-2 border-primary/30 bg-white px-4 py-3 text-text focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200 cursor-pointer"
            disabled={loading}
          >
            <option value="">{t('selectOption')}</option>
            {IMAGE_STYLE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {t(opt.labelKey)}
              </option>
            ))}
          </select>

          <label htmlFor="numEpisodes" className="flex items-center gap-2 text-sm font-semibold text-text mt-4 mb-2">
            <IconEpisodes className="text-primary shrink-0" size={18} />
            {t('episodesLabel')}
          </label>
          <input
            id="numEpisodes"
            type="number"
            min={1}
            max={10}
            value={numEpisodes}
            onChange={(e) => setNumEpisodes(Number(e.target.value) ?? 1)}
            className="w-full rounded-xl border-2 border-primary/30 bg-white px-4 py-3 text-text focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200"
            disabled={loading}
            aria-describedby={numEpisodes < 1 || numEpisodes > 10 ? 'episodes-hint' : undefined}
          />
          {(numEpisodes < 1 || numEpisodes > 10) && (
            <p id="episodes-hint" className="mt-1 text-amber-600 text-sm">
              {t('episodesRangeHint')}
            </p>
          )}
        </div>

        {error && (
          <p className="mt-4 text-red-600 text-sm" role="alert">
            {error}
          </p>
        )}

        {loading && (
          <div className="mt-6 space-y-2" role="status" aria-live="polite" aria-label={t('creating')}>
            <div className="flex justify-between text-sm">
              <span className="font-medium text-text">{t('creating')}</span>
              <span className="font-semibold text-primary tabular-nums">{Math.min(100, Math.round(progress))}%</span>
            </div>
            <div className="h-2.5 w-full rounded-full bg-primary/20 overflow-hidden">
              <div
                className="h-full rounded-full bg-primary transition-[width] duration-300 ease-out"
                style={{ width: `${Math.min(100, progress)}%` }}
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !topic.trim() || numEpisodes < 1 || numEpisodes > 10}
          className="mt-6 w-full rounded-xl bg-primary py-3.5 px-5 font-semibold text-white shadow-lg shadow-primary/30 hover:bg-primary-dark hover:shadow-xl hover:shadow-primary/35 hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0 transition-all duration-200 cursor-pointer"
        >
          {loading ? t('creating') : t('createStory')}
        </button>
      </form>

      <nav className="mt-6 sm:mt-8 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
        <Link
          to="/stories"
          className="inline-flex items-center gap-2 rounded-xl border-2 border-secondary/60 bg-secondary/10 px-5 py-2.5 font-medium text-text hover:bg-secondary/25 hover:border-secondary focus:outline-none focus:ring-2 focus:ring-secondary focus:ring-offset-2 transition-all duration-200 cursor-pointer"
        >
          <IconLibrary className="text-secondary shrink-0" size={20} />
          {t('viewSavedStories')}
        </Link>
      </nav>
    </div>
  )
}
