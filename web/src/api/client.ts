import type {
  GenerateStoryRequest,
  GenerateStoryResponse,
  StoryListItem,
  GetStoryResponse,
} from './types'

const BASE = '/api'

export async function generateStory(
  body: GenerateStoryRequest
): Promise<GenerateStoryResponse> {
  const res = await fetch(`${BASE}/story/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || res.statusText || 'สร้างเรื่องไม่สำเร็จ')
  }
  return res.json()
}

export async function getStory(storyId: string): Promise<GetStoryResponse> {
  const res = await fetch(`${BASE}/story/${storyId}`)
  if (!res.ok) throw new Error('ไม่พบเรื่อง')
  return res.json()
}

export async function listStories(
  limit = 20,
  offset = 0
): Promise<StoryListItem[]> {
  const res = await fetch(`${BASE}/stories?limit=${limit}&offset=${offset}`)
  if (!res.ok) return []
  return res.json()
}

export async function exportVideo(storyId: string): Promise<Blob> {
  const res = await fetch(`${BASE}/story/export-video`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ storyId }),
  })
  if (!res.ok) throw new Error('ส่งออกวิดีโอไม่สำเร็จ')
  return res.blob()
}
