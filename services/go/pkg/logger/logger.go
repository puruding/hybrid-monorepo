package logger

import (
	"fmt"
	"log"
	"os"
	"time"
)

// Level represents log level
type Level int

const (
	DEBUG Level = iota
	INFO
	WARN
	ERROR
)

// Logger is a simple structured logger
type Logger struct {
	service string
	level   Level
	logger  *log.Logger
}

// New creates a new logger for a service
func New(service string) *Logger {
	return &Logger{
		service: service,
		level:   INFO,
		logger:  log.New(os.Stdout, "", 0),
	}
}

// SetLevel sets the minimum log level
func (l *Logger) SetLevel(level Level) {
	l.level = level
}

func (l *Logger) log(level Level, levelStr, msg string) {
	if level < l.level {
		return
	}
	timestamp := time.Now().Format(time.RFC3339)
	l.logger.Printf("[%s] %s [%s] %s", timestamp, levelStr, l.service, msg)
}

// Debug logs a debug message
func (l *Logger) Debug(msg string) {
	l.log(DEBUG, "DEBUG", msg)
}

// Info logs an info message
func (l *Logger) Info(msg string) {
	l.log(INFO, "INFO", msg)
}

// Warn logs a warning message
func (l *Logger) Warn(msg string) {
	l.log(WARN, "WARN", msg)
}

// Error logs an error message
func (l *Logger) Error(msg string) {
	l.log(ERROR, "ERROR", msg)
}

// Errorf logs a formatted error message
func (l *Logger) Errorf(format string, args ...interface{}) {
	l.log(ERROR, "ERROR", fmt.Sprintf(format, args...))
}
