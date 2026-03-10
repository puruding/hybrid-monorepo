package errors

import "fmt"

// AppError represents an application error with code
type AppError struct {
	Code    string
	Message string
	Err     error
}

// Error implements the error interface
func (e *AppError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("[%s] %s: %v", e.Code, e.Message, e.Err)
	}
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

// Unwrap returns the wrapped error
func (e *AppError) Unwrap() error {
	return e.Err
}

// New creates a new AppError
func New(code, message string) *AppError {
	return &AppError{
		Code:    code,
		Message: message,
	}
}

// Wrap wraps an existing error with additional context
func Wrap(err error, code, message string) *AppError {
	return &AppError{
		Code:    code,
		Message: message,
		Err:     err,
	}
}

// Common error codes
const (
	ErrNotFound     = "NOT_FOUND"
	ErrUnauthorized = "UNAUTHORIZED"
	ErrForbidden    = "FORBIDDEN"
	ErrInternal     = "INTERNAL_ERROR"
	ErrValidation   = "VALIDATION_ERROR"
)

// NotFound creates a not found error
func NotFound(message string) *AppError {
	return New(ErrNotFound, message)
}

// Unauthorized creates an unauthorized error
func Unauthorized(message string) *AppError {
	return New(ErrUnauthorized, message)
}

// Internal creates an internal error
func Internal(message string) *AppError {
	return New(ErrInternal, message)
}

// Validation creates a validation error
func Validation(message string) *AppError {
	return New(ErrValidation, message)
}
