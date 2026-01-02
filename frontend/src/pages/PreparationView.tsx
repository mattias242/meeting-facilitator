import { useState } from 'react'
import IDOARRTUpload from '../components/preparation/IDOARRTUpload'
import IDOARRTPreview from '../components/preparation/IDOARRTPreview'
import ValidationErrors from '../components/preparation/ValidationErrors'
import TestModeUpload from '../components/preparation/TestModeUpload'
import { useDarkMode } from '../hooks/useDarkMode'
import { meetingApi } from '../services/api'
import { CreateMeetingResponse } from '../types/meeting'
import './PreparationView.css'

export default function PreparationView() {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<CreateMeetingResponse | null>(null)
  const [testAudioFile, setTestAudioFile] = useState<File | null>(null)
  const [testChunkDuration, setTestChunkDuration] = useState(2)
  const { isDark, toggle: toggleDarkMode } = useDarkMode()

  const handleFileSelect = async (content: string) => {
    setIsLoading(true)
    setResult(null)

    try {
      const response = await meetingApi.create(content)
      setResult(response.data)
    } catch (error) {
      console.error('Failed to create meeting:', error)
      setResult({
        success: false,
        validation_errors: ['Ett fel uppstod vid uppladdning. Försök igen.'],
        parsed_idoarrt: null,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="preparation-view">
      <header className="view-header">
        <div>
          <h1>Förbered Möte</h1>
          <p className="view-description">
            Ladda upp din IDOARRT markdown-fil för att skapa och validera ett nytt möte.
          </p>
        </div>
        <button className="theme-toggle" onClick={toggleDarkMode} aria-label="Toggle dark mode">
          {isDark ? '☀️' : '🌙'}
        </button>
      </header>

      <IDOARRTUpload onFileSelect={handleFileSelect} isLoading={isLoading} />

      {result && !result.success && (
        <ValidationErrors errors={result.validation_errors} />
      )}

      {result && result.success && result.parsed_idoarrt && (
        <>
          <TestModeUpload
            onAudioFileSelect={setTestAudioFile}
            audioFile={testAudioFile}
            chunkDurationMinutes={testChunkDuration}
            onChunkDurationChange={setTestChunkDuration}
          />

          <IDOARRTPreview
            data={result.parsed_idoarrt}
            meeting={result.meeting}
            testAudioFile={testAudioFile}
            testChunkDuration={testChunkDuration}
          />
        </>
      )}
    </div>
  )
}
