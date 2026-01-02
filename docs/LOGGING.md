# Logs Directory

This directory contains application logs for debugging and monitoring.

## Backend Logs

### Log Files
- `app.log` - General application logs (DEBUG level)
- `errors.log` - Error and exception logs only
- `security.log` - Authentication and authorization events
- `api.log` - HTTP API request/response logs
- `audio.log` - Audio processing and transcription events
- `claude.log` - Claude API interactions

### Log Rotation
Logs are not automatically rotated. Monitor file sizes and implement rotation if needed.

## Frontend Logs

Frontend logs are stored in:
- Browser console (development)
- LocalStorage (persistent)
- Downloadable via `window.logger.exportLogs()`

### Frontend Log Categories
- User actions (button clicks, navigation)
- API requests (HTTP calls)
- Audio recording events
- WebSocket connections
- Meeting lifecycle events

## Viewing Logs

### Backend
```bash
# View real-time logs
tail -f logs/app.log

# View error logs
tail -f logs/errors.log

# View API logs
tail -f logs/api.log

# Search logs
grep "ERROR" logs/app.log
grep "meeting_id" logs/api.log
```

### Frontend
```javascript
// In browser console
window.logger.getLogs()        // Recent logs in memory
window.logger.exportLogs()     // Download all logs
window.logger.clearLogs()       // Clear all logs
```

## Log Levels

### Backend (Python logging)
- `DEBUG` - Detailed development information
- `INFO` - General application flow
- `WARNING` - Unexpected situations
- `ERROR` - Serious errors and exceptions

### Frontend
- `DEBUG` - Development debugging
- `INFO` - General information
- `WARN` - Warning messages
- `ERROR` - Error messages

## Security Logging

Security events are logged separately in `logs/security.log`:
- Login attempts (success/failure)
- Token validation
- Authorization failures
- Suspicious activities

## Performance Monitoring

API requests include timing information:
- Request duration in milliseconds
- Response status codes
- Error tracking

## Troubleshooting

### Common Issues
1. **Permission denied**: Check directory permissions
2. **Disk full**: Monitor log file sizes
3. **Missing logs**: Check logging configuration

### Log Analysis
```bash
# Find errors in last hour
find logs/ -name "*.log" -exec grep -H "$(date -d '1 hour ago' '+%Y-%m-%d %H')" {} \;

# Count error occurrences
grep -c "ERROR" logs/app.log

# Find specific meeting logs
grep "meeting_id_123" logs/*.log
```
