import { useNavigate } from 'react-router-dom'
import { IDOARRTData, Meeting } from '../../types/meeting'

interface IDOARRTPreviewProps {
  data: IDOARRTData
  meeting?: Meeting
  onStartMeeting?: () => void
}

export default function IDOARRTPreview({ data, meeting, onStartMeeting }: IDOARRTPreviewProps) {
  const navigate = useNavigate()

  const handleStartMeeting = () => {
    if (meeting) {
      navigate(`/meeting/${meeting.id}`)
    } else if (onStartMeeting) {
      onStartMeeting()
    }
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
        <div className="preview-actions">
          <button className="start-button" onClick={handleStartMeeting}>
            Starta Möte
          </button>
        </div>
      )}

      <style>{`
        .idoarrt-preview {
          background-color: #2d3748;
          border-radius: 8px;
          padding: 2rem;
          margin: 1.5rem 0;
        }

        .preview-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid #4a5568;
        }

        .check-icon {
          width: 32px;
          height: 32px;
          color: #48bb78;
          flex-shrink: 0;
        }

        .preview-header h2 {
          margin: 0;
          font-size: 1.5rem;
          font-weight: 600;
          color: #48bb78;
        }

        .preview-section {
          margin-bottom: 2rem;
        }

        .preview-section h3 {
          margin: 0 0 1rem 0;
          font-size: 1.125rem;
          font-weight: 600;
          color: #63b3ed;
        }

        .intent-text {
          margin: 0;
          font-size: 1rem;
          line-height: 1.6;
          color: #e2e8f0;
          background-color: #1a202c;
          padding: 1rem;
          border-radius: 4px;
        }

        .outcomes-list,
        .rules-list {
          margin: 0;
          padding-left: 1.5rem;
          list-style: disc;
        }

        .outcomes-list li,
        .rules-list li {
          margin: 0.5rem 0;
          color: #e2e8f0;
          line-height: 1.6;
        }

        .agenda-table {
          background-color: #1a202c;
          border-radius: 4px;
          overflow: hidden;
        }

        .agenda-item,
        .agenda-total {
          display: grid;
          grid-template-columns: 2rem 1fr auto;
          gap: 1rem;
          padding: 0.75rem 1rem;
          border-bottom: 1px solid #2d3748;
          align-items: center;
        }

        .agenda-item:last-of-type {
          border-bottom: 2px solid #4a5568;
        }

        .agenda-total {
          border-bottom: none;
          font-weight: 600;
          background-color: #2d3748;
        }

        .agenda-number {
          color: #a0aec0;
          font-weight: 500;
        }

        .agenda-topic {
          color: #e2e8f0;
        }

        .agenda-time {
          color: #63b3ed;
          font-weight: 500;
          text-align: right;
        }

        .roles-list {
          display: grid;
          gap: 0.75rem;
        }

        .role-item {
          display: flex;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          background-color: #1a202c;
          border-radius: 4px;
        }

        .role-name {
          color: #63b3ed;
          font-weight: 500;
          min-width: 120px;
        }

        .role-person {
          color: #e2e8f0;
        }

        .preview-actions {
          margin-top: 2rem;
          padding-top: 1.5rem;
          border-top: 2px solid #4a5568;
          display: flex;
          justify-content: center;
        }

        .start-button {
          padding: 1rem 2rem;
          font-size: 1.125rem;
          font-weight: 600;
          color: white;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        .start-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        }

        .start-button:active {
          transform: translateY(0);
        }
      `}</style>
    </div>
  )
}
