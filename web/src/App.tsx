import { Routes, Route, Link } from 'react-router-dom'
import { LangSwitcher, useLang } from './context/LangContext'
import Home from './pages/Home'
import StoryView from './pages/StoryView'
import StoryList from './pages/StoryList'

function SkipToMain() {
  const { t } = useLang()
  return (
    <a
      href="#main-content"
      className="sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[100] focus:px-4 focus:py-3 focus:bg-primary focus:text-white focus:rounded-xl focus:shadow-lg focus:outline-none focus:w-auto focus:h-auto focus:m-0 focus:overflow-visible focus:[clip:auto]"
    >
      {t('skipToMain')}
    </a>
  )
}

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <SkipToMain />
      <header className="flex justify-between items-center p-2 sm:p-3 border-b border-primary/10 bg-white/50 shrink-0">
        <Link to="/" className="flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded-lg">
          <img src="/logo.png" alt="" className="h-8 w-8 sm:h-9 sm:w-9 object-contain" width="36" height="36" />
        </Link>
        <LangSwitcher />
      </header>
      <main id="main-content" className="flex-1" tabIndex={-1}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/story/:storyId" element={<StoryView />} />
          <Route path="/stories" element={<StoryList />} />
        </Routes>
      </main>
    </div>
  )
}
