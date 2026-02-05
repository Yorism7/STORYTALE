import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useLang } from '../context/LangContext'
import { listStories } from '../api/client'
import type { StoryListItem } from '../api/types'

export default function StoryList() {
  const { t, locale } = useLang()
  const [stories, setStories] = useState<StoryListItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listStories()
      .then(setStories)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  function formatDate(iso: string) {
    try {
      return new Date(iso).toLocaleDateString(locale === 'th' ? 'th-TH' : 'en-US', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      })
    } catch {
      return iso
    }
  }

  return (
    <div className="min-h-full p-4 sm:p-6">
      <header className="flex items-center gap-4 mb-8">
        <Link
          to="/"
          className="text-primary font-medium hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded cursor-pointer"
        >
          {t('back')}
        </Link>
        <h1 className="text-2xl font-bold text-text">{t('storyListTitle')}</h1>
      </header>

      {loading ? (
        <p className="text-text/70">{t('loading')}</p>
      ) : stories.length === 0 ? (
        <p className="text-text/70">{t('noStories')}</p>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {stories.map((s) => (
            <li key={s.storyId}>
              <Link
                to={`/story/${s.storyId}`}
                className="block rounded-2xl bg-white/80 shadow-lg border border-primary/20 p-4 hover:shadow-xl hover:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-200 cursor-pointer"
              >
                <h2 className="font-semibold text-text truncate">{s.title}</h2>
                <p className="text-sm text-text/70 mt-1 truncate">{s.topic}</p>
                <p className="text-xs text-text/50 mt-2">
                  {s.num_episodes} {t('episodesCount')} · {formatDate(s.created_at)}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
