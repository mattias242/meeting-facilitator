import { useState, useRef, useCallback } from 'react'

export interface AudioRecorderOptions {
  chunkDurationMinutes?: number
  onChunkReady?: (chunk: Blob, chunkNumber: number, durationSeconds: number) => void
  onError?: (error: Error) => void
}

export interface AudioRecorderState {
  isRecording: boolean
  isPaused: boolean
  currentChunkNumber: number
  totalDurationSeconds: number
  error: string | null
}

export interface AudioRecorderControls {
  startRecording: () => Promise<void>
  stopRecording: () => void
  pauseRecording: () => void
  resumeRecording: () => void
}

export default function useAudioRecorder(
  options: AudioRecorderOptions = {}
): [AudioRecorderState, AudioRecorderControls] {
  const {
    chunkDurationMinutes = 2,
    onChunkReady,
    onError,
  } = options

  const [state, setState] = useState<AudioRecorderState>({
    isRecording: false,
    isPaused: false,
    currentChunkNumber: 0,
    totalDurationSeconds: 0,
    error: null,
  })

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const chunkStartTimeRef = useRef<number>(0)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const isFinalizingRef = useRef<boolean>(false)

  const startRecording = useCallback(async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      // Create MediaRecorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm'

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
      })
      mediaRecorderRef.current = mediaRecorder

      chunksRef.current = []
      chunkStartTimeRef.current = Date.now()

      // Handle data available event
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      // Handle errors
      mediaRecorder.onerror = (event) => {
        const error = new Error(`MediaRecorder error: ${event}`)
        setState((prev) => ({ ...prev, error: error.message }))
        onError?.(error)
      }

      // Start recording with timeslice to get data periodically
      mediaRecorder.start(1000) // Get data every second

      setState((prev) => ({
        ...prev,
        isRecording: true,
        isPaused: false,
        error: null,
      }))

      // Set interval to create chunks
      const chunkDurationMs = chunkDurationMinutes * 60 * 1000
      intervalRef.current = setInterval(() => {
        if (mediaRecorderRef.current?.state === 'recording') {
          finalizeChunk()
        }
      }, chunkDurationMs)
    } catch (error) {
      const err = error as Error
      setState((prev) => ({ ...prev, error: err.message }))
      onError?.(err)
    }
  }, [chunkDurationMinutes, onError])

  const finalizeChunk = useCallback(() => {
    // Guard against concurrent calls
    if (isFinalizingRef.current) return
    if (chunksRef.current.length === 0) return

    isFinalizingRef.current = true

    // Create blob from chunks
    const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
    const durationSeconds = (Date.now() - chunkStartTimeRef.current) / 1000

    // Reset for next chunk BEFORE emitting (prevent race condition)
    const currentChunks = chunksRef.current
    chunksRef.current = []
    chunkStartTimeRef.current = Date.now()

    // Emit chunk
    setState((prev) => {
      const newChunkNumber = prev.currentChunkNumber + 1
      onChunkReady?.(blob, newChunkNumber, durationSeconds)
      return {
        ...prev,
        currentChunkNumber: newChunkNumber,
        totalDurationSeconds: prev.totalDurationSeconds + durationSeconds,
      }
    })

    isFinalizingRef.current = false
  }, [onChunkReady])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()

      // Finalize last chunk
      finalizeChunk()

      // Clear interval
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }

      // Stop all tracks
      streamRef.current?.getTracks().forEach((track) => track.stop())
      streamRef.current = null
      mediaRecorderRef.current = null

      setState((prev) => ({
        ...prev,
        isRecording: false,
        isPaused: false,
      }))
    }
  }, [finalizeChunk])

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause()
      setState((prev) => ({ ...prev, isPaused: true }))
    }
  }, [])

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume()
      setState((prev) => ({ ...prev, isPaused: false }))
    }
  }, [])

  return [
    state,
    {
      startRecording,
      stopRecording,
      pauseRecording,
      resumeRecording,
    },
  ]
}
