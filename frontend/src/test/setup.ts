import '@testing-library/jest-dom'

// Mock Web Audio API
Object.defineProperty(window, 'MediaRecorder', {
  writable: true,
  value: class MediaRecorder {
    static isTypeSupported(mimeType: string): boolean {
      return mimeType === 'audio/webm' || mimeType === 'audio/webm;codecs=opus'
    }
    
    constructor(stream: MediaStream, options?: MediaRecorderOptions) {
      this.stream = stream
      this.mimeType = options?.mimeType || 'audio/webm'
    }
    
    stream: MediaStream
    mimeType: string
    state: 'inactive' | 'recording' | 'paused' = 'inactive'
    
    start(timeslice?: number): void {
      this.state = 'recording'
      // Mock dataavailable event
      setTimeout(() => {
        this.ondataavailable?.(new Blob(['mock audio data'], { type: this.mimeType }))
      }, timeslice || 1000)
    }
    
    stop(): void {
      this.state = 'inactive'
    }
    
    pause(): void {
      this.state = 'paused'
    }
    
    resume(): void {
      this.state = 'recording'
    }
    
    ondataavailable: ((event: BlobEvent) => void) | null = null
    onerror: ((event: Event) => void) | null = null
  }
})

// Mock getUserMedia
Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: vi.fn().mockResolvedValue({
      getTracks: () => [{ stop: vi.fn() }]
    })
  }
})

// Mock WebSocket
Object.defineProperty(global, 'WebSocket', {
  writable: true,
  value: class MockWebSocket {
    url: string
    readyState: number = 1 // OPEN
    onopen: ((event: Event) => void) | null = null
    onclose: ((event: CloseEvent) => void) | null = null
    onmessage: ((event: MessageEvent) => void) | null = null
    onerror: ((event: Event) => void) | null = null
    
    constructor(url: string) {
      this.url = url
    }
    
    send(data: string): void {
      // Mock send
    }
    
    close(): void {
      this.readyState = 3 // CLOSED
      this.onclose?.(new CloseEvent('close'))
    }
  }
})
