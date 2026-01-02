/** Simple frontend logging utility. */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  context?: any;
}

class SimpleLogger {
  private logs: LogEntry[] = [];
  private maxLogs = 1000; // Keep last 1000 logs in memory
  
  constructor(private minLevel: LogLevel = LogLevel.INFO) {
    // Setup error handling
    window.addEventListener('error', (event) => {
      this.error('Unhandled Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack,
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.error('Unhandled Promise Rejection', {
        reason: event.reason,
        stack: event.reason?.stack,
      });
    });
  }

  private formatMessage(level: string, message: string, context?: any): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? ` | ${JSON.stringify(context)}` : '';
    return `${timestamp} [${level}]: ${message}${contextStr}`;
  }

  private log(level: LogLevel, levelName: string, message: string, context?: any) {
    if (level < this.minLevel) return;

    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: levelName,
      message,
      context,
    };

    // Add to memory logs
    this.logs.push(logEntry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // Console output
    const formattedMessage = this.formatMessage(levelName, message, context);
    
    switch (level) {
      case LogLevel.DEBUG:
        console.debug(formattedMessage);
        break;
      case LogLevel.INFO:
        console.info(formattedMessage);
        break;
      case LogLevel.WARN:
        console.warn(formattedMessage);
        break;
      case LogLevel.ERROR:
        console.error(formattedMessage);
        break;
    }

    // Store in localStorage for persistence
    this.storeLog(logEntry);
  }

  private storeLog(logEntry: LogEntry) {
    try {
      const storedLogs = this.getStoredLogs();
      storedLogs.push(logEntry);
      
      // Keep only last 500 logs in localStorage
      if (storedLogs.length > 500) {
        storedLogs.splice(0, storedLogs.length - 500);
      }
      
      localStorage.setItem('meeting-facilitator-logs', JSON.stringify(storedLogs));
    } catch (error) {
      console.error('Failed to store log:', error);
    }
  }

  private getStoredLogs(): LogEntry[] {
    try {
      const stored = localStorage.getItem('meeting-facilitator-logs');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  debug(message: string, context?: any) {
    this.log(LogLevel.DEBUG, 'DEBUG', message, context);
  }

  info(message: string, context?: any) {
    this.log(LogLevel.INFO, 'INFO', message, context);
  }

  warn(message: string, context?: any) {
    this.log(LogLevel.WARN, 'WARN', message, context);
  }

  error(message: string, context?: any) {
    this.log(LogLevel.ERROR, 'ERROR', message, context);
  }

  // Specialized logging functions
  userAction(action: string, details: any = {}) {
    this.info('USER_ACTION', { action, ...details });
  }

  apiRequest(method: string, url: string, status?: number, duration?: number, error?: string) {
    const context: any = { method, url };
    if (status) context.status = status;
    if (duration) context.duration = duration;
    if (error) context.error = error;

    if (error) {
      this.error('API_REQUEST_ERROR', context);
    } else {
      this.info('API_REQUEST', context);
    }
  }

  audioEvent(event: string, details: any = {}) {
    this.info('AUDIO_EVENT', { event, ...details });
  }

  meetingEvent(event: string, meetingId: string, details: any = {}) {
    this.info('MEETING_EVENT', { event, meetingId, ...details });
  }

  webSocketEvent(event: string, details: any = {}) {
    this.info('WEBSOCKET_EVENT', { event, ...details });
  }

  // Get logs for debugging
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  getStoredLogsAll(): LogEntry[] {
    return this.getStoredLogs();
  }

  // Export logs to file (for debugging)
  exportLogs(): string {
    const allLogs = [...this.getStoredLogsAll(), ...this.logs];
    return JSON.stringify(allLogs, null, 2);
  }

  // Clear logs
  clearLogs() {
    this.logs = [];
    localStorage.removeItem('meeting-facilitator-logs');
  }
}

// Create singleton logger instance
const logger = new SimpleLogger(LogLevel.DEBUG);

// Development helper: expose logger to window for debugging
if (typeof window !== 'undefined') {
  (window as any).logger = logger;
}

export default logger;
