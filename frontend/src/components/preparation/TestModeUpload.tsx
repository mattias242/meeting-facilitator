import { useState, useRef } from 'react'
import './TestModeUpload.css'

interface TestModeUploadProps {
  onAudioFileSelect: (file: File) => void
  audioFile: File | null
  chunkDurationMinutes: number
  onChunkDurationChange: (minutes: number) => void
}

export default function TestModeUpload({
  onAudioFileSelect,
  audioFile,
  chunkDurationMinutes,
  onChunkDurationChange,
}: TestModeUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file: File) => {
    // Accept common audio formats
    const validTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/webm', 'audio/ogg', 'audio/m4a']
    const isAudio = validTypes.includes(file.type) ||
                    file.name.match(/\.(mp3|wav|webm|ogg|m4a)$/i)

    if (!isAudio) {
      alert('Vänligen välj en ljudfil (MP3, WAV, WebM, OGG, M4A)')
      return
    }

    onAudioFileSelect(file)
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className="test-mode-upload card">
      <h3 className="test-mode-title">🧪 Test Mode (Valfritt)</h3>
      <p className="test-mode-description">
        Ladda upp en ljudfil för att testa AI-facilitering utan att spela in live
      </p>

      <div
        className={`test-upload-zone ${dragActive ? 'drag-active' : ''} ${audioFile ? 'has-file' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*,.mp3,.wav,.webm,.ogg,.m4a"
          onChange={handleChange}
          style={{ display: 'none' }}
        />

        <div className="test-upload-content">
          {audioFile ? (
            <>
              <svg
                className="file-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                />
              </svg>
              <p className="file-name">{audioFile.name}</p>
              <p className="file-size">{formatFileSize(audioFile.size)}</p>
              <p className="file-hint">Klicka för att välja annan fil</p>
            </>
          ) : (
            <>
              <svg
                className="upload-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="upload-text">
                Dra och släpp ljudfil här eller klicka för att välja
              </p>
              <p className="upload-hint">MP3, WAV, WebM, OGG, M4A</p>
            </>
          )}
        </div>
      </div>

      {audioFile && (
        <div className="test-settings">
          <label className="setting-item">
            <span className="setting-label">Chunk-storlek (minuter):</span>
            <input
              type="number"
              min="1"
              max="10"
              value={chunkDurationMinutes}
              onChange={(e) => onChunkDurationChange(Number(e.target.value))}
              className="setting-input"
            />
          </label>
        </div>
      )}
    </div>
  )
}
