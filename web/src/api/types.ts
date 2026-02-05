export type ImageModel = 'flux' | 'zimage'
export type StoryLang = 'en' | 'th'

export interface GenerateStoryRequest {
  topic: string
  num_episodes: number
  story_lang?: StoryLang
  image_model?: ImageModel
  image_style?: string | null
}

export interface EpisodeOut {
  text: string
  imageUrl: string
}

export interface GenerateStoryResponse {
  storyId: string
  title: string
  episodes: EpisodeOut[]
}

export interface StoryListItem {
  storyId: string
  topic: string
  title: string
  num_episodes: number
  created_at: string
}

export interface GetStoryResponse {
  storyId: string
  topic: string
  title: string
  num_episodes: number
  created_at: string
  episodes: EpisodeOut[]
}
