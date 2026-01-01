export interface AgendaItem {
  topic: string
  duration_minutes: number
}

export interface IDOARRTData {
  intent: string
  desired_outcomes: string[]
  agenda: AgendaItem[]
  roles: Record<string, string>
  rules: string[]
  total_duration_minutes: number
}

export interface Meeting {
  id: string
  created_at: string
  intent: string
  desired_outcomes: string[]
  agenda: AgendaItem[]
  roles: Record<string, string>
  rules: string[]
  total_duration_minutes: number
  status: 'preparation' | 'active' | 'completed'
  started_at: string | null
  ended_at: string | null
  time_extensions_seconds: number
}

export interface CreateMeetingResponse {
  success: boolean
  meeting?: Meeting
  validation_errors: string[]
  parsed_idoarrt: IDOARRTData | null
}
