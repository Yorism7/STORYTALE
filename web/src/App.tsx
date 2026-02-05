import { Routes, Route } from 'react-router-dom'
import { LangSwitcher } from './context/LangContext'
import Home from './pages/Home'
import StoryView from './pages/StoryView'
import StoryList from './pages/StoryList'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-end items-center p-2 sm:p-3 border-b border-primary/10 bg-white/50 shrink-0">
        <LangSwitcher />
      </header>
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/story/:storyId" element={<StoryView />} />
          <Route path="/stories" element={<StoryList />} />
        </Routes>
      </main>
    </div>
  )
}
