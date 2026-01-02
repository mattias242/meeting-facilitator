import { useState, useRef } from 'react'
import { audioApi } from '../../services/api'
import './UploadRecording.css'

interface UploadRecordingProps {
  meetingId: string
  onUploadComplete: () => void
}

export default function UploadRecording({ meetingId, onUploadComplete }: UploadRecordingProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [chunkDuration, setChunkDuration] = useState(2)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setError(null)
    setProgress('Läser ljudfil...')

    try {
      const formData = new FormData()
      formData.append('audio_file', file)
      formData.append('chunk_duration_minutes', chunkDuration.toString())

      setProgress('Delar upp i chunks...')
      const response = await audioApi.uploadRecording(meetingId, formData)

      setProgress(`✓ Klart! ${response.data.chunks_created} chunks skapade`)

      // Wait a bit then complete
      setTimeout(() => {
        onUploadComplete()
      }, 1500)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Upload misslyckades'
      setError(errorMsg)
      setProgress(null)
    } finally {
      setIsUploading(false)
    }
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="upload-recording">
      <h3>🧪 Test-funktion: Ladda upp färdig inspelning</h3>
      <p>Ladda upp en ljudfil som delas upp i chunks automatiskt</p>

      <div className="upload-controls">
        <label>
          Chunk-längd (minuter):
          <input
            type="number"
            min="1"
            max="10"
            value={chunkDuration}
            onChange={(e) => setChunkDuration(Number(e.target.value))}
            disabled={isUploading}
          />
        </label>

        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        <button
          onClick={handleButtonClick}
          disabled={isUploading}
          className="upload-btn"
        >
          {isUploading ? 'Bearbetar...' : 'Välj ljudfil'}
        </button>
      </div>

      {progress && (
        <div className="progress-message">
          {progress}
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="upload-hint">
        <strong>Tips:</strong> Stödda format: MP3, WAV, M4A, WebM, OGG
      </div>
    </div>
  )
}
