import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Meeting API
export const meetingApi = {
  create: (idoarrtMarkdown: string) =>
    api.post('/api/v1/meetings', { idoarrt_markdown: idoarrtMarkdown }),

  get: (meetingId: string) =>
    api.get(`/api/v1/meetings/${meetingId}`),

  start: (meetingId: string) =>
    api.patch(`/api/v1/meetings/${meetingId}/start`),

  end: (meetingId: string) =>
    api.patch(`/api/v1/meetings/${meetingId}/end`),

  extend: (meetingId: string, seconds: number) =>
    api.patch(`/api/v1/meetings/${meetingId}/extend`, { seconds }),
}

// Audio API
export const audioApi = {
  uploadChunk: (meetingId: string, formData: FormData) =>
    api.post(`/api/v1/meetings/${meetingId}/audio-chunks`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
}

// Protocol API
export const protocolApi = {
  get: (meetingId: string) =>
    api.get(`/api/v1/meetings/${meetingId}/protocol`),

  generate: (meetingId: string) =>
    api.post(`/api/v1/meetings/${meetingId}/protocol/generate`),
}
