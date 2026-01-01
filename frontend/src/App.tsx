import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import PreparationView from './pages/PreparationView'
import LiveMeetingView from './pages/LiveMeetingView'
import WrapUpView from './pages/WrapUpView'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route path="/" element={<PreparationView />} />
          <Route path="/meeting/:meetingId" element={<LiveMeetingView />} />
          <Route path="/meeting/:meetingId/wrap-up" element={<WrapUpView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
