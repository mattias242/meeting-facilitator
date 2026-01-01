import { useState, useRef } from 'react'

interface IDOARRTUploadProps {
  onFileSelect: (content: string) => void
  isLoading?: boolean
}

export default function IDOARRTUpload({ onFileSelect, isLoading }: IDOARRTUploadProps) {
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
    if (!file.name.endsWith('.md')) {
      alert('Vänligen välj en markdown (.md) fil')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      onFileSelect(content)
    }
    reader.readAsText(file)
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="idoarrt-upload">
      <div
        className={`upload-zone ${dragActive ? 'drag-active' : ''} ${isLoading ? 'loading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".md"
          onChange={handleChange}
          style={{ display: 'none' }}
          disabled={isLoading}
        />

        <div className="upload-content">
          {isLoading ? (
            <>
              <div className="spinner"></div>
              <p>Analyserar IDOARRT-fil...</p>
            </>
          ) : (
            <>
              <svg
                className="upload-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="upload-text">
                Dra och släpp din IDOARRT markdown-fil här
                <br />
                eller klicka för att välja fil
              </p>
              <p className="upload-hint">Endast .md filer</p>
            </>
          )}
        </div>
      </div>

      <style>{`
        .idoarrt-upload {
          width: 100%;
          max-width: 600px;
          margin: 0 auto;
        }

        .upload-zone {
          border: 2px dashed #4a5568;
          border-radius: 8px;
          padding: 3rem 2rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s ease;
          background-color: #2d3748;
        }

        .upload-zone:hover:not(.loading) {
          border-color: #63b3ed;
          background-color: #374151;
        }

        .upload-zone.drag-active {
          border-color: #63b3ed;
          background-color: #374151;
          transform: scale(1.02);
        }

        .upload-zone.loading {
          cursor: not-allowed;
          opacity: 0.7;
        }

        .upload-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }

        .upload-icon {
          width: 48px;
          height: 48px;
          color: #63b3ed;
        }

        .upload-text {
          font-size: 1rem;
          color: #e2e8f0;
          margin: 0;
          line-height: 1.6;
        }

        .upload-hint {
          font-size: 0.875rem;
          color: #a0aec0;
          margin: 0;
        }

        .spinner {
          width: 48px;
          height: 48px;
          border: 4px solid #4a5568;
          border-top-color: #63b3ed;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
