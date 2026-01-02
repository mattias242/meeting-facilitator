import { useParams } from 'react-router-dom'
import { useDarkMode } from '../hooks/useDarkMode'
import './WrapUpView.css'

export default function WrapUpView() {
  const { meetingId } = useParams<{ meetingId: string }>()
  const { isDark, toggle: toggleDarkMode } = useDarkMode()

  return (
    <div className="wrap-up-view">
      <header className="wrap-up-header">
        <div>
          <h1>Mötes-Protokoll</h1>
          <p className="meeting-id-display">Meeting ID: {meetingId}</p>
        </div>
        <button className="theme-toggle" onClick={toggleDarkMode} aria-label="Toggle dark mode">
          {isDark ? '☀️' : '🌙'}
        </button>
      </header>

      <div className="wrap-up-content">
        <div className="card protocol-placeholder">
          <p>Protokollgenerering kommer snart...</p>
          <p className="text-secondary">
            Här kommer du att kunna se sammanfattning, beslut och nästa steg från mötet.
          </p>
        </div>
      </div>
    </div>
  )
}
