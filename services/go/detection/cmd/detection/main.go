package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/example/monorepo/services/go/pkg/logger"
)

func main() {
	l := logger.New("detection")
	l.Info("Starting detection service...")

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "OK")
	})

	http.HandleFunc("/detect", func(w http.ResponseWriter, r *http.Request) {
		l.Info("Detection request received")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"detected": true}`)
	})

	l.Info("Listening on :8081")
	if err := http.ListenAndServe(":8081", nil); err != nil {
		log.Fatal(err)
	}
}
