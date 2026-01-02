import { useState, useEffect } from 'react'

interface UseCountdownTimerProps {
  startedAt: Date | null
  totalDurationMinutes: number
  isActive: boolean
}

interface CountdownTimerState {
  remainingSeconds: number
  percentageComplete: number
  isOvertime: boolean
  formattedTime: string
}

export function useCountdownTimer({
  startedAt,
  totalDurationMinutes,
  isActive,
}: UseCountdownTimerProps): CountdownTimerState {
  const [remainingSeconds, setRemainingSeconds] = useState(0)

  useEffect(() => {
    if (!isActive || !startedAt) {
      setRemainingSeconds(totalDurationMinutes * 60)
      return
    }

    const updateTimer = () => {
      const now = new Date()
      const elapsed = Math.floor((now.getTime() - startedAt.getTime()) / 1000)
      const total = totalDurationMinutes * 60
      const remaining = total - elapsed

      setRemainingSeconds(remaining)
    }

    // Update immediately
    updateTimer()

    // Update every second
    const interval = setInterval(updateTimer, 1000)

    return () => clearInterval(interval)
  }, [startedAt, totalDurationMinutes, isActive])

  const totalSeconds = totalDurationMinutes * 60
  const percentageComplete = totalSeconds > 0
    ? Math.min(100, Math.max(0, ((totalSeconds - remainingSeconds) / totalSeconds) * 100))
    : 0

  const isOvertime = remainingSeconds < 0

  // Format time as MM:SS or -MM:SS if overtime
  const absSeconds = Math.abs(remainingSeconds)
  const minutes = Math.floor(absSeconds / 60)
  const seconds = absSeconds % 60
  const formattedTime = `${isOvertime ? '-' : ''}${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`

  return {
    remainingSeconds,
    percentageComplete,
    isOvertime,
    formattedTime,
  }
}
