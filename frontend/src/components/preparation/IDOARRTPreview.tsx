import { useNavigate } from 'react-router-dom'
import { IDOARRTData, Meeting } from '../../types/meeting'
import UploadRecording from './UploadRecording'
import './IDOARRTPreview.css'

interface IDOARRTPreviewProps {
  data: IDOARRTData
  meeting?: Meeting
  onStartMeeting?: () => void
  onRecordingUploaded?: () => void
  testAudioFile?: File | null
  testChunkDuration?: number
}

export default function IDOARRTPreview({
  data,
  meeting,
  onStartMeeting,
  onRecordingUploaded,
  testAudioFile,
  testChunkDuration
}: IDOARRTPreviewProps) {
  const navigate = useNavigate()

  const handleStartMeeting = () => {
    if (meeting) {
      // Pass test mode data via navigation state
      navigate(`/meeting/${meeting.id}`, {
        state: {
          testMode: testAudioFile ? {
            audioFile: testAudioFile,
            chunkDuration: testChunkDuration || 2
          } : null
        }
      })
    } else if (onStartMeeting) {
      onStartMeeting()
    }
  }

  const handleRecordingUpload = () => {
    if (meeting) {
      // Navigate to the completed meeting view
      navigate(`/meeting/${meeting.id}`)
    }
    onRecordingUploaded?.()
  }

  return (
    <div className="idoarrt-preview">
      <div className="preview-header">
        <svg
          className="check-icon"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h2>IDOARRT Validerad ✓</h2>
      </div>

      <div className="preview-section">
        <h3>Intent (Syfte)</h3>
        <p className="intent-text">{data.intent}</p>
      </div>

      <div className="preview-section">
        <h3>Desired Outcomes (Önskade Resultat)</h3>
        <ul className="outcomes-list">
          {data.desired_outcomes.map((outcome, index) => (
            <li key={index}>{outcome}</li>
          ))}
        </ul>
      </div>

      <div className="preview-section">
        <h3>Agenda (Dagordning)</h3>
        <div className="agenda-table">
          {data.agenda.map((item, index) => (
            <div key={index} className="agenda-item">
              <span className="agenda-number">{index + 1}.</span>
              <span className="agenda-topic">{item.topic}</span>
              <span className="agenda-time">{item.duration_minutes} min</span>
            </div>
          ))}
          <div className="agenda-total">
            <span className="agenda-topic">Total tid</span>
            <span className="agenda-time">{data.total_duration_minutes} min</span>
          </div>
        </div>
      </div>

      <div className="preview-section">
        <h3>Roles (Roller)</h3>
        <div className="roles-list">
          {Object.entries(data.roles).map(([role, person]) => (
            <div key={role} className="role-item">
              <span className="role-name">{role}:</span>
              <span className="role-person">{person}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="preview-section">
        <h3>Rules (Regler)</h3>
        <ul className="rules-list">
          {data.rules.map((rule, index) => (
            <li key={index}>{rule}</li>
          ))}
        </ul>
      </div>

      {meeting && (
        <>
          <div className="preview-actions">
            <button className="btn-primary start-button" onClick={handleStartMeeting}>
              {testAudioFile ? '🧪 Starta Test-Möte' : 'Starta Möte'}
            </button>
          </div>

          <UploadRecording
            meetingId={meeting.id}
            onUploadComplete={handleRecordingUpload}
          />
        </>
      )}
    </div>
  )
}
