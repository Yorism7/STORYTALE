import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLang } from '../context/LangContext'
import { generateStory } from '../api/client'

export default function Home() {
  const navigate = useNavigate()
  const { t } = useLang()
  const [topic, setTopic] = useState('')
  const [numEpisodes, setNumEpisodes] = useState(5)
  const [storyLang, setStoryLang] = useState<'en' | 'th'>('en')
  const [imageModel, setImageModel] = useState<'flux' | 'zimage'>('flux')
  const [imageStyle, setImageStyle] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!topic.trim()) return
    setError('')
    setLoading(true)
    try {
      const data = await generateStory({
        topic: topic.trim(),
        num_episodes: numEpisodes,
        story_lang: storyLang,
        image_model: imageModel,
        image_style: imageStyle || undefined,
      })
      navigate(`/story/${data.storyId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errorGeneric'))
      console.error('[StoryTale] generate error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-full flex flex-col items-center justify-center p-4 sm:p-6">
      <header className="text-center mb-8">
        <h1 className="text-3xl sm:text-4xl font-bold text-text mb-2">
          {t('appTitle')}
        </h1>
        <p className="text-lg text-text/80">{t('appTagline')}</p>
      </header>

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl bg-white/80 shadow-lg shadow-primary/20 p-6 sm:p-8 border border-primary/30"
      >
        <label className="block text-sm font-medium text-text mb-2">
          {t('topicLabel')}
        </label>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder={t('topicPlaceholder')}
          className="w-full rounded-xl border border-primary/40 bg-surface/50 px-4 py-3 text-text placeholder:text-text/50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"
          disabled={loading}
          maxLength={500}
        />

        <label className="block text-sm font-medium text-text mt-4 mb-2">
          {t('storyLangLabel')}
        </label>
        <select
          value={storyLang}
          onChange={(e) => setStoryLang(e.target.value as 'en' | 'th')}
          className="w-full rounded-xl border border-primary/40 bg-surface/50 px-4 py-3 text-text focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-200 cursor-pointer"
          disabled={loading}
        >
          <option value="en">{t('storyLangEn')}</option>
          <option value="th">{t('storyLangTh')}</option>
        </select>

        <label className="block text-sm font-medium text-text mt-4 mb-2">
          {t('imageModelLabel')}
        </label>
        <select
          value={imageModel}
          onChange={(e) => setImageModel(e.target.value as 'flux' | 'zimage')}
          className="w-full rounded-xl border border-primary/40 bg-surface/50 px-4 py-3 text-text focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-200 cursor-pointer"
          disabled={loading}
        >
          <option value="flux">Flux Schnell</option>
          <option value="zimage">Z-Image Turbo</option>
        </select>

        <label className="block text-sm font-medium text-text mt-4 mb-2">
          {t('imageStyleLabel')}
        </label>
        <select
          value={imageStyle}
          onChange={(e) => setImageStyle(e.target.value)}
          className="w-full rounded-xl border border-primary/40 bg-surface/50 px-4 py-3 text-text focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-200 cursor-pointer"
          disabled={loading}
        >
          <option value="">{t('selectOption')}</option>
          <option value="cartoon style">การ์ตูน</option>
          <option value="watercolor painting">วาดน้ำ</option>
          <option value="retro vintage">เรโทร</option>
        </select>

        <label className="block text-sm font-medium text-text mt-4 mb-2">
          {t('episodesLabel')}
        </label>
        <input
          type="number"
          min={1}
          max={10}
          value={numEpisodes}
          onChange={(e) => setNumEpisodes(Number(e.target.value) || 5)}
          className="w-full rounded-xl border border-primary/40 bg-surface/50 px-4 py-3 text-text focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"
          disabled={loading}
        />

        {error && (
          <p className="mt-3 text-red-600 text-sm" role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading || !topic.trim()}
          className="mt-6 w-full rounded-xl bg-primary py-3 px-4 font-medium text-white shadow-md hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
        >
          {loading ? t('creating') : t('createStory')}
        </button>
      </form>

      <nav className="mt-8">
        <a
          href="/stories"
          className="text-secondary font-medium hover:underline focus:outline-none focus:ring-2 focus:ring-secondary rounded cursor-pointer"
        >
          {t('viewSavedStories')}
        </a>
      </nav>
    </div>
  )
}
