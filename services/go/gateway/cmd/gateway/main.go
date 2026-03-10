package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/example/monorepo/services/go/pkg/logger"
)

func main() {
	l := logger.New("gateway")
	l.Info("Starting gateway service...")

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "OK")
	})

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		l.Info("Received request: " + r.URL.Path)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "Gateway Service")
	})

	l.Info("Listening on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
