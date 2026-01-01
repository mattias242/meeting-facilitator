import { useParams } from 'react-router-dom'

export default function WrapUpView() {
  const { meetingId } = useParams<{ meetingId: string }>()

  return (
    <div className="wrap-up-view">
      <h1>Mötes-Protokoll</h1>
      <p>Meeting ID: {meetingId}</p>
      {/* TODO: Implement protocol display */}
    </div>
  )
}
