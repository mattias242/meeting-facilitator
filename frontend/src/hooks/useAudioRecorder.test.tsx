import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import useAudioRecorder from '../hooks/useAudioRecorder'

// Test component to use the hook
function TestComponent({ onChunkReady, onError }: { onChunkReady?: Function; onError?: Function }) {
  const [state, controls] = useAudioRecorder({
    chunkDurationMinutes: 2,
    onChunkReady,
    onError,
  })

  return (
    <div>
      <div data-testid="is-recording">{state.isRecording.toString()}</div>
      <div data-testid="is-paused">{state.isPaused.toString()}</div>
      <div data-testid="chunk-number">{state.currentChunkNumber}</div>
      <div data-testid="error">{state.error || ''}</div>
      <button onClick={controls.startRecording}>Start</button>
      <button onClick={controls.stopRecording}>Stop</button>
      <button onClick={controls.pauseRecording}>Pause</button>
      <button onClick={controls.resumeRecording}>Resume</button>
    </div>
  )
}

describe('useAudioRecorder', () => {
  let mockChunkReady: ReturnType<typeof vi.fn>
  let mockError: ReturnType<typeof vi.fn>

  beforeEach(() => {
    mockChunkReady = vi.fn()
    mockError = vi.fn()
    vi.clearAllMocks()
  })

  it('initializes with correct default state', () => {
    render(<TestComponent />)
    
    expect(screen.getByTestId('is-recording')).toHaveTextContent('false')
    expect(screen.getByTestId('is-paused')).toHaveTextContent('false')
    expect(screen.getByTestId('chunk-number')).toHaveTextContent('0')
    expect(screen.getByTestId('error')).toHaveTextContent('')
  })

  it('starts recording when start button is clicked', async () => {
    const user = userEvent.setup()
    render(<TestComponent onChunkReady={mockChunkReady} />)
    
    await user.click(screen.getByText('Start'))
    
    expect(screen.getByTestId('is-recording')).toHaveTextContent('true')
    expect(screen.getByTestId('is-paused')).toHaveTextContent('false')
  })

  it('stops recording when stop button is clicked', async () => {
    const user = userEvent.setup()
    render(<TestComponent onChunkReady={mockChunkReady} />)
    
    await user.click(screen.getByText('Start'))
    await user.click(screen.getByText('Stop'))
    
    expect(screen.getByTestId('is-recording')).toHaveTextContent('false')
  })

  it('pauses recording when pause button is clicked', async () => {
    const user = userEvent.setup()
    render(<TestComponent />)
    
    await user.click(screen.getByText('Start'))
    await user.click(screen.getByText('Pause'))
    
    expect(screen.getByTestId('is-paused')).toHaveTextContent('true')
  })

  it('resumes recording when resume button is clicked', async () => {
    const user = userEvent.setup()
    render(<TestComponent />)
    
    await user.click(screen.getByText('Start'))
    await user.click(screen.getByText('Pause'))
    await user.click(screen.getByText('Resume'))
    
    expect(screen.getByTestId('is-paused')).toHaveTextContent('false')
  })

  it('calls onChunkReady when chunk is ready', async () => {
    const user = userEvent.setup()
    render(<TestComponent onChunkReady={mockChunkReady} />)
    
    await user.click(screen.getByText('Start'))
    
    // Wait for chunk to be ready (mock MediaRecorder triggers after 1 second)
    await waitFor(() => {
      expect(mockChunkReady).toHaveBeenCalledWith(
        expect.any(Blob),
        expect.any(Number),
        expect.any(Number)
      )
    }, { timeout: 2000 })
  })

  it('updates chunk number when chunk is ready', async () => {
    const user = userEvent.setup()
    render(<TestComponent onChunkReady={mockChunkReady} />)
    
    await user.click(screen.getByText('Start'))
    
    await waitFor(() => {
      expect(screen.getByTestId('chunk-number')).toHaveTextContent('1')
    }, { timeout: 2000 })
  })

  it('handles recording errors', async () => {
    // Mock getUserMedia to reject
    const mockGetUserMedia = vi.fn().mockRejectedValue(new Error('Permission denied'))
    Object.defineProperty(navigator, 'mediaDevices', {
      writable: true,
      value: { getUserMedia: mockGetUserMedia }
    })

    const user = userEvent.setup()
    render(<TestComponent onError={mockError} />)
    
    await user.click(screen.getByText('Start'))
    
    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Permission denied')
      expect(mockError).toHaveBeenCalledWith(expect.any(Error))
    })
  })

  it('does not start recording if already recording', async () => {
    const user = userEvent.setup()
    render(<TestComponent />)
    
    await user.click(screen.getByText('Start'))
    await user.click(screen.getByText('Start')) // Click again
    
    expect(screen.getByTestId('is-recording')).toHaveTextContent('true')
    // Should still be recording, not reset
  })

  it('handles custom chunk duration', async () => {
    function TestComponentCustomDuration() {
      const [state, controls] = useAudioRecorder({
        chunkDurationMinutes: 5,
        onChunkReady: mockChunkReady,
      })

      return (
        <div>
          <button onClick={controls.startRecording}>Start</button>
          <div data-testid="chunk-number">{state.currentChunkNumber}</div>
        </div>
      )
    }

    const user = userEvent.setup()
    render(<TestComponentCustomDuration />)
    
    await user.click(screen.getByText('Start'))
    
    // Should still work with custom duration
    expect(screen.getByTestId('chunk-number')).toHaveTextContent('0')
  })
})
