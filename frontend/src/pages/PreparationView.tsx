import { useState } from 'react'
import IDOARRTUpload from '../components/preparation/IDOARRTUpload'
import IDOARRTPreview from '../components/preparation/IDOARRTPreview'
import ValidationErrors from '../components/preparation/ValidationErrors'
import { meetingApi } from '../services/api'
import { CreateMeetingResponse } from '../types/meeting'

export default function PreparationView() {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<CreateMeetingResponse | null>(null)

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
        <h1>Förbered Möte</h1>
        <p className="view-description">
          Ladda upp din IDOARRT markdown-fil för att skapa och validera ett nytt möte.
        </p>
      </header>

      <IDOARRTUpload onFileSelect={handleFileSelect} isLoading={isLoading} />

      {result && !result.success && (
        <ValidationErrors errors={result.validation_errors} />
      )}

      {result && result.success && result.parsed_idoarrt && (
        <IDOARRTPreview
          data={result.parsed_idoarrt}
          meeting={result.meeting}
        />
      )}

      <style>{`
        .preparation-view {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }

        .view-header {
          text-align: center;
          margin-bottom: 3rem;
        }

        .view-header h1 {
          font-size: 2.5rem;
          font-weight: 700;
          margin: 0 0 1rem 0;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .view-description {
          font-size: 1.125rem;
          color: #a0aec0;
          margin: 0;
        }
      `}</style>
    </div>
  )
}
