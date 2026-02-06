import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useLang } from '../context/LangContext'
import { getStory, exportVideo } from '../api/client'
import type { GetStoryResponse } from '../api/types'

const API_BASE = '/api'

export default function StoryView() {
  const { storyId } = useParams<{ storyId: string }>()
  const navigate = useNavigate()
  const { t } = useLang()
  const [story, setStory] = useState<GetStoryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [index, setIndex] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [exportError, setExportError] = useState('')
  const [linkCopied, setLinkCopied] = useState(false)
  const [audioLoading, setAudioLoading] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  useEffect(() => {
    if (!linkCopied) return
    const t = setTimeout(() => setLinkCopied(false), 2500)
    return () => clearTimeout(t)
  }, [linkCopied])

  useEffect(() => {
    if (!storyId) return
    getStory(storyId)
      .then(setStory)
      .catch((err) => {
        setError(err instanceof Error ? err.message : t('loadFailed'))
        console.error('[StoryTale] getStory error:', err)
      })
      .finally(() => setLoading(false))
  }, [storyId])

  if (loading) {
    return (
      <div className="min-h-full flex items-center justify-center">
        <p className="text-text/80">{t('loading')}</p>
      </div>
    )
  }
  if (error || !story) {
    return (
      <div className="min-h-full flex flex-col items-center justify-center gap-4">
        <p className="text-red-600">{error || t('storyNotFound')}</p>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="rounded-xl bg-primary px-4 py-2 text-white cursor-pointer hover:opacity-90 transition-opacity"
        >
          {t('backHome')}
        </button>
      </div>
    )
  }

  const episode = story.episodes[index]
  const hasPrev = index > 0
  const hasNext = index < story.episodes.length - 1

  return (
    <div className="min-h-full flex flex-col bg-surface">
      <header className="relative flex items-center justify-between p-4 border-b border-primary/20 bg-white/60 shrink-0">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="text-primary font-medium hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded cursor-pointer"
          >
            {t('back')}
          </button>
          <button
            type="button"
            onClick={() => {
              const url = `${window.location.origin}/story/${story.storyId}`
              navigator.clipboard.writeText(url).then(() => setLinkCopied(true))
            }}
            className="text-secondary font-medium hover:underline focus:outline-none focus:ring-2 focus:ring-secondary rounded cursor-pointer text-sm min-h-[44px] min-w-[44px] inline-flex items-center justify-center"
          >
            {t('shareLink')}
          </button>
        </div>
        {linkCopied && (
          <p
            role="status"
            aria-live="polite"
            className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-1.5 rounded-lg bg-secondary/90 text-white text-sm shadow-lg z-10"
          >
            {t('linkCopied')}
          </p>
        )}
        <h1 className="text-lg font-semibold text-text truncate max-w-[45%] sm:max-w-[60%]">
          {story.title}
        </h1>
        <span className="text-sm text-text/70 w-16 text-right">
          {index + 1}/{story.episodes.length}
        </span>
      </header>

      <main className="flex-1 flex flex-col sm:flex-row items-stretch overflow-hidden p-4 gap-4">
        <div
          key={index}
          className="flex-1 flex flex-col sm:flex-row items-stretch gap-4 min-h-0 animate-fade-in"
        >
        <section className="flex-1 min-h-[200px] sm:min-h-0 flex items-center justify-center rounded-2xl bg-white/80 shadow-lg overflow-hidden border border-primary/20">
          {episode.imageUrl ? (
            <img
              src={episode.imageUrl}
              alt={`${t('episodeAlt')} ${index + 1}`}
              className="max-w-full max-h-[50vh] sm:max-h-full object-contain"
            />
          ) : (
            <span className="text-text/50">{t('noImage')}</span>
          )}
        </section>
        <section className="flex-1 flex flex-col justify-center rounded-2xl bg-white/80 shadow-lg p-6 border border-primary/20">
          <p className="text-text leading-relaxed whitespace-pre-wrap">
            {episode.text}
          </p>
          <button
            type="button"
            onClick={() => {
              if (playing) {
                audioRef.current?.pause()
                setPlaying(false)
                return
              }
              setAudioLoading(true)
              const url = `${API_BASE}/story/${story!.storyId}/episode/${index}/audio`
              const audio = new Audio(url)
              audioRef.current = audio
              audio
                .play()
                .then(() => {
                  setPlaying(true)
                  setAudioLoading(false)
                })
                .catch((err) => {
                  console.error('[StoryTale] audio play error:', err)
                  setAudioLoading(false)
                })
              audio.onended = () => setPlaying(false)
            }}
            disabled={audioLoading}
            className="mt-4 rounded-xl bg-secondary px-4 py-2 text-white font-medium cursor-pointer hover:opacity-90 disabled:opacity-70 transition-opacity min-h-[44px]"
          >
            {audioLoading ? t('loading') : playing ? t('stopAudio') : t('playAudio')}
          </button>
        </section>
        </div>
      </main>

      <footer className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between p-4 border-t border-primary/20 bg-white/60 gap-4 shrink-0">
        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
            disabled={!hasPrev}
            className="rounded-xl bg-primary/80 px-4 py-2 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:enabled:bg-primary transition-colors cursor-pointer"
          >
            {t('prev')}
          </button>
          <button
            type="button"
            onClick={() => setIndex((i) => Math.min(story.episodes.length - 1, i + 1))}
            disabled={!hasNext}
            className="rounded-xl bg-primary/80 px-4 py-2 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:enabled:bg-primary transition-colors cursor-pointer"
          >
            {t('next')}
          </button>
        </div>
        <div className="flex flex-col items-end gap-1">
          {exportError && (
            <p role="alert" className="text-red-600 text-sm">
              {exportError}
            </p>
          )}
          <button
            type="button"
            onClick={async () => {
              setExporting(true)
              setExportError('')
              try {
                const blob = await exportVideo(story.storyId)
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `${story.title || 'story'}.mp4`
                a.click()
                URL.revokeObjectURL(url)
              } catch (e) {
                console.error('[StoryTale] export video error:', e)
                setExportError(t('exportVideoError'))
              } finally {
                setExporting(false)
              }
            }}
            disabled={exporting}
            className="rounded-xl bg-secondary px-4 py-2 text-white font-medium cursor-pointer hover:opacity-90 disabled:opacity-60 transition-opacity focus:outline-none focus:ring-2 focus:ring-secondary focus:ring-offset-2 min-h-[44px]"
          >
            {exporting ? t('exporting') : t('exportVideo')}
          </button>
        </div>
      </footer>
    </div>
  )
}
