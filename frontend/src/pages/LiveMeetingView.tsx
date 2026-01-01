import { useParams } from 'react-router-dom'

export default function LiveMeetingView() {
  const { meetingId } = useParams<{ meetingId: string }>()

  return (
    <div className="live-meeting-view">
      <h1>Live Möte</h1>
      <p>Meeting ID: {meetingId}</p>
      {/* TODO: Implement live meeting components */}
    </div>
  )
}
