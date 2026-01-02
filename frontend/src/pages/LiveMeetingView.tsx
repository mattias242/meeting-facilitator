import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { meetingApi, audioApi } from '../services/api'
import useAudioRecorder from '../hooks/useAudioRecorder'
import { useCountdownTimer } from '../hooks/useCountdownTimer'
import { useDarkMode } from '../hooks/useDarkMode'
import { useTestModeAudio } from '../hooks/useTestModeAudio'
import type { Meeting } from '../types/meeting'
import './LiveMeetingView.css'

export default function LiveMeetingView() {
  const { meetingId } = useParams<{ meetingId: string }>()
  const navigate = useNavigate()
  const location = useLocation()

  const [meeting, setMeeting] = useState<Meeting | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [chunkDurationMinutes, setChunkDurationMinutes] = useState(2)
  const [uploadedChunks, setUploadedChunks] = useState<number[]>([])
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [audioChunks, setAudioChunks] = useState<any[]>([])
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null)

  // Extract test mode config from navigation state
  const testModeConfig = (location.state as any)?.testMode || null

  // Dark mode
  const { isDark, toggle: toggleDarkMode } = useDarkMode()

  // Countdown timer
  const timer = useCountdownTimer({
    startedAt: meeting?.started_at ? new Date(meeting.started_at) : null,
    totalDurationMinutes: meeting?.total_duration_minutes || 60,
    isActive: meeting?.status === 'active',
  })

  // Handle chunk upload
  const handleChunkReady = useCallback(
    async (blob: Blob, chunkNumber: number, durationSeconds: number) => {
      if (!meetingId) return

      try {
        const formData = new FormData()
        formData.append('audio_file', blob, `chunk-${chunkNumber}.webm`)
        formData.append('chunk_number', chunkNumber.toString())
        formData.append('duration_seconds', durationSeconds.toString())

        await audioApi.uploadChunk(meetingId, formData)
        setUploadedChunks((prev) => [...prev, chunkNumber])
        setUploadError(null)
        console.log(`Chunk ${chunkNumber} uploaded successfully`)
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Upload failed'
        setUploadError(errorMsg)
        console.error('Failed to upload chunk:', err)
      }
    },
    [meetingId]
  )

  // Initialize audio recorder (only for live mode)
  const [audioState, audioControls] = useAudioRecorder({
    chunkDurationMinutes,
    onChunkReady: handleChunkReady,
    onError: (err) => setError(err.message),
  })

  // Initialize test mode audio (only if test mode config exists)
  const [testModeState, testModeControls] = useTestModeAudio(
    testModeConfig,
    handleChunkReady
  )

  // Fetch meeting data
  useEffect(() => {
    if (!meetingId) return

    const fetchMeeting = async () => {
      try {
        const response = await meetingApi.get(meetingId)
        setMeeting(response.data)
        setIsLoading(false)
      } catch (err) {
        setError('Kunde inte ladda mötet')
        setIsLoading(false)
      }
    }

    fetchMeeting()
  }, [meetingId])

  // Fetch audio chunks if meeting is completed
  useEffect(() => {
    if (!meetingId || !meeting || meeting.status !== 'completed') return

    const fetchChunks = async () => {
      try {
        const response = await audioApi.listChunks(meetingId)
        setAudioChunks(response.data)
      } catch (err) {
        console.error('Failed to fetch audio chunks:', err)
      }
    }

    fetchChunks()
  }, [meetingId, meeting?.status])

  // Start meeting and recording
  const handleStartMeeting = async () => {
    if (!meetingId) return

    try {
      // Start meeting in backend
      await meetingApi.start(meetingId)

      // Update local state
      setMeeting((prev) => prev ? { ...prev, status: 'active' } : null)

      // Start audio recording
      await audioControls.startRecording()
    } catch (err) {
      setError('Kunde inte starta mötet')
    }
  }

  // End meeting and recording
  const handleEndMeeting = async () => {
    if (!meetingId) return

    try {
      // Stop recording first
      audioControls.stopRecording()

      // Wait for last chunk to upload (give it 1 second)
      await new Promise(resolve => setTimeout(resolve, 1000))

      // End meeting in backend
      await meetingApi.end(meetingId)

      // Navigate to wrap-up view
      navigate(`/meeting/${meetingId}/wrap-up`)
    } catch (err) {
      setError('Kunde inte avsluta mötet')
    }
  }

  // Extend meeting time
  const handleExtendTime = async () => {
    if (!meetingId) return

    try {
      await meetingApi.extend(meetingId, 300) // 5 minutes
      alert('Mötet förlängt med 5 minuter')
    } catch (err) {
      setError('Kunde inte förlänga mötet')
    }
  }

  if (isLoading) {
    return <div className="loading">Laddar möte...</div>
  }

  if (!meeting) {
    return <div className="error">Mötet kunde inte hittas</div>
  }

  return (
    <div className="live-meeting-view">
      <header className="meeting-header">
        <div>
          <h1>Live Möte</h1>
          <div className="meeting-status">
            Status: <span className={`status-badge ${meeting.status}`}>{meeting.status}</span>
          </div>
        </div>
        <button className="theme-toggle" onClick={toggleDarkMode} aria-label="Toggle dark mode">
          {isDark ? '☀️' : '🌙'}
        </button>
      </header>

      {meeting.status === 'active' && (
        <div className="countdown-timer">
          <div className="timer-display">
            <div className={`timer-time ${timer.isOvertime ? 'overtime' : ''}`}>
              {timer.formattedTime}
            </div>
            <div className="timer-label">
              {timer.isOvertime ? 'Övertid' : 'Tid kvar'}
            </div>
          </div>
          <div className="timer-progress">
            <div
              className={`timer-progress-bar ${
                timer.percentageComplete > 75 ? 'warning' : ''
              } ${timer.isOvertime ? 'overtime' : ''}`}
              style={{ width: `${Math.min(100, timer.percentageComplete)}%` }}
            />
          </div>
        </div>
      )}

      <div className="meeting-info">
        <h2>Intent</h2>
        <p>{meeting.intent}</p>

        <h3>Önskade Utfall</h3>
        <ul>
          {meeting.desired_outcomes.map((outcome, index) => (
            <li key={index}>{outcome}</li>
          ))}
        </ul>
      </div>

      {testModeConfig ? (
        /* TEST MODE */
        <div className="recording-section">
          <h2>🧪 Test Mode</h2>

          <div className="test-mode-info">
            <div className="status-item">
              <strong>Ljudfil:</strong> {testModeConfig.audioFile.name}
            </div>
            <div className="status-item">
              <strong>Progress:</strong> {testModeState.currentChunkNumber} / {testModeState.totalChunks} chunks
            </div>
            <div className="status-item">
              <strong>Uppladdade:</strong> {uploadedChunks.length}
            </div>
            {testModeState.totalChunks > 0 && (
              <div className="status-item">
                <strong>Framsteg:</strong>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${testModeState.progress}%` }}
                  />
                </div>
                {testModeState.progress.toFixed(0)}%
              </div>
            )}
          </div>

          {testModeState.error && (
            <div className="error-message">{testModeState.error}</div>
          )}
          {uploadError && (
            <div className="error-message">Uppladdningsfel: {uploadError}</div>
          )}

          <div className="recording-controls">
            {meeting.status === 'preparation' && (
              <button onClick={handleStartMeeting} className="btn-primary">
                Starta Test-Möte
              </button>
            )}

            {meeting.status === 'active' && (
              <>
                <button
                  onClick={testModeControls.sendNextChunk}
                  disabled={testModeState.isProcessing || testModeState.isComplete}
                  className="btn-primary"
                >
                  {testModeState.isProcessing ? 'Bearbetar...' :
                   testModeState.isComplete ? 'Alla chunks skickade ✓' :
                   `Skicka Chunk ${testModeState.currentChunkNumber + 1}/${testModeState.totalChunks}`}
                </button>

                {testModeState.isComplete && (
                  <button onClick={testModeControls.reset} className="btn-secondary">
                    Återställ
                  </button>
                )}

                <button onClick={handleExtendTime} className="btn-secondary">
                  Förläng +5 min
                </button>

                <button onClick={handleEndMeeting} className="btn-danger">
                  Avsluta Möte
                </button>
              </>
            )}
          </div>
        </div>
      ) : (
        /* LIVE MODE */
        <div className="recording-section">
          <h2>Inspelning</h2>

          <div className="recording-config">
            <label>
              Chunk-längd (minuter):
              <input
                type="number"
                min="1"
                max="10"
                value={chunkDurationMinutes}
                onChange={(e) => setChunkDurationMinutes(Number(e.target.value))}
                disabled={audioState.isRecording}
              />
            </label>
          </div>

          <div className="recording-status">
            <div className="status-item">
              <strong>Status:</strong>{' '}
              {audioState.isRecording
                ? (audioState.isPaused ? 'Pausad' : 'Spelar in...')
                : 'Stoppad'}
            </div>
            <div className="status-item">
              <strong>Nuvarande chunk:</strong> {audioState.currentChunkNumber}
            </div>
            <div className="status-item">
              <strong>Uppladdade chunks:</strong> {uploadedChunks.length}
            </div>
            <div className="status-item">
              <strong>Total tid:</strong> {Math.floor(audioState.totalDurationSeconds / 60)} min {Math.floor(audioState.totalDurationSeconds % 60)} sek
            </div>
          </div>

          {audioState.error && (
            <div className="error-message">Inspelningsfel: {audioState.error}</div>
          )}
          {uploadError && (
            <div className="error-message">Uppladdningsfel: {uploadError}</div>
          )}
          {error && (
            <div className="error-message">{error}</div>
          )}

          <div className="recording-controls">
            {meeting.status === 'preparation' && (
              <button onClick={handleStartMeeting} className="btn-primary">
                Starta Möte & Inspelning
              </button>
            )}

            {meeting.status === 'active' && (
              <>
                {!audioState.isRecording ? (
                  <button onClick={audioControls.startRecording} className="btn-primary">
                    Starta Inspelning
                  </button>
                ) : audioState.isPaused ? (
                  <button onClick={audioControls.resumeRecording} className="btn-success">
                    Återuppta
                  </button>
                ) : (
                  <button onClick={audioControls.pauseRecording} className="btn-warning">
                    Pausa
                  </button>
                )}

                <button onClick={handleExtendTime} className="btn-secondary">
                  Förläng +5 min
                </button>

                <button onClick={handleEndMeeting} className="btn-danger">
                  Avsluta Möte
                </button>
              </>
            )}
          </div>
        </div>
      )}

      <div className="chunks-list">
        <h3>{meeting.status === 'completed' ? 'Spela Upp Mötet' : 'Uppladdade Audio Chunks'}</h3>

        {meeting.status === 'completed' ? (
          // Show playable chunks for completed meetings
          audioChunks.length === 0 ? (
            <p>Inga ljudinspelningar tillgängliga</p>
          ) : (
            <div className="audio-player-list">
              {audioChunks.map((chunk) => (
                <div key={chunk.id} className="audio-chunk-player">
                  <div className="chunk-info">
                    <strong>Chunk #{chunk.chunk_number}</strong>
                    <span>{Math.floor(chunk.duration_seconds / 60)}:{String(Math.floor(chunk.duration_seconds % 60)).padStart(2, '0')}</span>
                  </div>
                  <audio
                    controls
                    preload="metadata"
                    onPlay={() => setCurrentlyPlaying(chunk.id)}
                    onPause={() => setCurrentlyPlaying(null)}
                    onError={(e) => console.error('Audio error:', e)}
                  >
                    <source src={audioApi.getChunkAudioUrl(chunk.id)} type="audio/webm; codecs=opus" />
                    Din webbläsare stödjer inte audio-uppspelning.
                  </audio>
                  {chunk.transcription && (
                    <div className="transcription">
                      <em>Transkription:</em> {chunk.transcription}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )
        ) : (
          // Show upload status during active meeting
          uploadedChunks.length === 0 ? (
            <p>Inga chunks uppladdade än</p>
          ) : (
            <ul>
              {uploadedChunks.map((chunkNum) => (
                <li key={chunkNum}>Chunk #{chunkNum} ✓</li>
              ))}
            </ul>
          )
        )}
      </div>
    </div>
  )
}
