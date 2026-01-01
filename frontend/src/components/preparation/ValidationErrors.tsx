interface ValidationErrorsProps {
  errors: string[]
}

export default function ValidationErrors({ errors }: ValidationErrorsProps) {
  if (errors.length === 0) return null

  return (
    <div className="validation-errors">
      <div className="error-header">
        <svg
          className="error-icon"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3>Valideringsfel</h3>
      </div>

      <ul className="error-list">
        {errors.map((error, index) => (
          <li key={index}>{error}</li>
        ))}
      </ul>

      <p className="error-hint">
        Rätta till felen ovan och ladda upp filen igen. Se{' '}
        <a href="/docs/IDOARRT-format.md" target="_blank" rel="noopener noreferrer">
          IDOARRT format guide
        </a>{' '}
        för hjälp.
      </p>

      <style>{`
        .validation-errors {
          background-color: #742a2a;
          border: 1px solid #fc8181;
          border-radius: 8px;
          padding: 1.5rem;
          margin: 1.5rem 0;
        }

        .error-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }

        .error-icon {
          width: 24px;
          height: 24px;
          color: #fc8181;
          flex-shrink: 0;
        }

        .error-header h3 {
          margin: 0;
          font-size: 1.125rem;
          font-weight: 600;
          color: #feb2b2;
        }

        .error-list {
          margin: 0 0 1rem 0;
          padding-left: 2.5rem;
          list-style: disc;
        }

        .error-list li {
          color: #fed7d7;
          margin: 0.5rem 0;
          line-height: 1.5;
        }

        .error-hint {
          margin: 0;
          font-size: 0.875rem;
          color: #feb2b2;
        }

        .error-hint a {
          color: #fbd38d;
          text-decoration: underline;
        }

        .error-hint a:hover {
          color: #fbd38d;
        }
      `}</style>
    </div>
  )
}
