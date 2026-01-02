import { useState, useEffect, useCallback, useRef } from 'react'

interface TestModeConfig {
  audioFile: File
  chunkDurationMinutes: number
}

interface TestModeState {
  currentChunkNumber: number
  totalChunks: number
  isProcessing: boolean
  isComplete: boolean
  error: string | null
  progress: number
}

interface TestModeControls {
  sendNextChunk: () => Promise<void>
  reset: () => void
}

/**
 * Hook for managing test mode audio chunking
 * Splits audio file into chunks and sends them manually on demand
 */
export function useTestModeAudio(
  config: TestModeConfig | null,
  onChunkReady: (blob: Blob, chunkNumber: number, durationSeconds: number) => Promise<void>
): [TestModeState, TestModeControls] {
  const [currentChunkNumber, setCurrentChunkNumber] = useState(0)
  const [totalChunks, setTotalChunks] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [audioBuffer, setAudioBuffer] = useState<AudioBuffer | null>(null)

  const audioContextRef = useRef<AudioContext | null>(null)

  // Load and decode audio file
  useEffect(() => {
    if (!config) {
      setAudioBuffer(null)
      setTotalChunks(0)
      setCurrentChunkNumber(0)
      setIsComplete(false)
      return
    }

    const loadAudio = async () => {
      try {
        setError(null)

        // Create audio context if needed
        if (!audioContextRef.current) {
          audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
        }

        // Read file as array buffer
        const arrayBuffer = await config.audioFile.arrayBuffer()

        // Decode audio data
        const buffer = await audioContextRef.current.decodeAudioData(arrayBuffer)
        setAudioBuffer(buffer)

        // Calculate total chunks
        const chunkDurationMinutes = config.chunkDurationMinutes || 2
        const chunkDurationSeconds = chunkDurationMinutes * 60
        const totalDuration = buffer.duration
        const chunks = Math.ceil(totalDuration / chunkDurationSeconds)
        setTotalChunks(chunks)
        setCurrentChunkNumber(0)
        setIsComplete(false)

        console.log(`Test mode: Loaded audio file (${totalDuration.toFixed(1)}s) - ${chunks} chunks of ${chunkDurationMinutes}min each`)
      } catch (err) {
        console.error('Failed to load audio file:', err)
        setError('Kunde inte ladda ljudfilen. Kontrollera att det är en giltig ljudfil.')
      }
    }

    loadAudio()
  }, [config])

  // Extract chunk from audio buffer
  const extractChunk = useCallback(async (chunkIndex: number): Promise<Blob | null> => {
    if (!audioBuffer || !config) return null

    try {
      const chunkDurationMinutes = config.chunkDurationMinutes || 2
      const chunkDurationSeconds = chunkDurationMinutes * 60
      const startTime = chunkIndex * chunkDurationSeconds
      const endTime = Math.min(startTime + chunkDurationSeconds, audioBuffer.duration)
      const actualDuration = endTime - startTime

      if (actualDuration <= 0) return null

      // Create new buffer for this chunk
      const sampleRate = audioBuffer.sampleRate
      const startSample = Math.floor(startTime * sampleRate)
      const endSample = Math.floor(endTime * sampleRate)
      const chunkLength = endSample - startSample

      const chunkBuffer = audioContextRef.current!.createBuffer(
        audioBuffer.numberOfChannels,
        chunkLength,
        sampleRate
      )

      // Copy audio data for each channel
      for (let channel = 0; channel < audioBuffer.numberOfChannels; channel++) {
        const sourceData = audioBuffer.getChannelData(channel)
        const chunkData = chunkBuffer.getChannelData(channel)
        for (let i = 0; i < chunkLength; i++) {
          chunkData[i] = sourceData[startSample + i]
        }
      }

      // Convert to WAV blob
      const wavBlob = await audioBufferToWav(chunkBuffer)
      return wavBlob
    } catch (err) {
      console.error('Failed to extract chunk:', err)
      throw err
    }
  }, [audioBuffer, config])

  // Send next chunk
  const sendNextChunk = useCallback(async () => {
    if (!audioBuffer || !config || isProcessing || isComplete) return

    if (currentChunkNumber >= totalChunks) {
      setIsComplete(true)
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
      const chunkBlob = await extractChunk(currentChunkNumber)

      if (!chunkBlob) {
        setIsComplete(true)
        setIsProcessing(false)
        return
      }

      const chunkDurationMinutes = config.chunkDurationMinutes || 2
      const chunkDurationSeconds = chunkDurationMinutes * 60

      console.log(`Sending test chunk ${currentChunkNumber + 1}/${totalChunks}`)

      await onChunkReady(chunkBlob, currentChunkNumber + 1, chunkDurationSeconds)

      setCurrentChunkNumber(prev => prev + 1)

      if (currentChunkNumber + 1 >= totalChunks) {
        setIsComplete(true)
      }
    } catch (err) {
      console.error('Failed to send chunk:', err)
      setError('Kunde inte skicka chunk. Försök igen.')
    } finally {
      setIsProcessing(false)
    }
  }, [audioBuffer, config, currentChunkNumber, totalChunks, isProcessing, isComplete, extractChunk, onChunkReady])

  const reset = useCallback(() => {
    setCurrentChunkNumber(0)
    setIsComplete(false)
    setError(null)
  }, [])

  const progress = totalChunks > 0 ? (currentChunkNumber / totalChunks) * 100 : 0

  return [
    {
      currentChunkNumber,
      totalChunks,
      isProcessing,
      isComplete,
      error,
      progress
    },
    {
      sendNextChunk,
      reset
    }
  ]
}

// Helper: Convert AudioBuffer to WAV Blob
async function audioBufferToWav(buffer: AudioBuffer): Promise<Blob> {
  const numberOfChannels = buffer.numberOfChannels
  const sampleRate = buffer.sampleRate
  const format = 1 // PCM
  const bitDepth = 16

  const bytesPerSample = bitDepth / 8
  const blockAlign = numberOfChannels * bytesPerSample

  const data = interleave(buffer)
  const dataLength = data.length * bytesPerSample
  const bufferLength = 44 + dataLength

  const arrayBuffer = new ArrayBuffer(bufferLength)
  const view = new DataView(arrayBuffer)

  // Write WAV header
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + dataLength, true)
  writeString(view, 8, 'WAVE')
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true) // fmt chunk size
  view.setUint16(20, format, true)
  view.setUint16(22, numberOfChannels, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * blockAlign, true) // byte rate
  view.setUint16(32, blockAlign, true)
  view.setUint16(34, bitDepth, true)
  writeString(view, 36, 'data')
  view.setUint32(40, dataLength, true)

  // Write audio data
  floatTo16BitPCM(view, 44, data)

  return new Blob([arrayBuffer], { type: 'audio/wav' })
}

function interleave(buffer: AudioBuffer): Float32Array {
  const numberOfChannels = buffer.numberOfChannels
  const length = buffer.length * numberOfChannels
  const result = new Float32Array(length)

  let offset = 0
  for (let i = 0; i < buffer.length; i++) {
    for (let channel = 0; channel < numberOfChannels; channel++) {
      result[offset++] = buffer.getChannelData(channel)[i]
    }
  }

  return result
}

function writeString(view: DataView, offset: number, string: string): void {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}

function floatTo16BitPCM(view: DataView, offset: number, input: Float32Array): void {
  for (let i = 0; i < input.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, input[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
  }
}
