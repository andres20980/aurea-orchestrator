package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/andres20980/aurea-orchestrator/internal/auth"
	"github.com/andres20980/aurea-orchestrator/internal/handlers"
	"github.com/andres20980/aurea-orchestrator/internal/middleware"
	"github.com/gorilla/mux"
)

func main() {
	// Load configuration from environment
	jwtSecret := os.Getenv("JWT_SECRET")
	if jwtSecret == "" {
		log.Fatal("JWT_SECRET environment variable is required")
	}

	tokenTTL := os.Getenv("TOKEN_TTL")
	if tokenTTL == "" {
		tokenTTL = "24h" // default to 24 hours
	}

	ttl, err := time.ParseDuration(tokenTTL)
	if err != nil {
		log.Fatalf("Invalid TOKEN_TTL format: %v", err)
	}

	// Initialize services
	authService := auth.NewService(jwtSecret, ttl)
	
	// Setup router
	r := mux.NewRouter()

	// Public endpoints
	r.HandleFunc("/login", handlers.Login(authService)).Methods("POST")

	// Protected endpoints
	api := r.PathPrefix("/api").Subrouter()
	api.Use(middleware.JWTAuth(jwtSecret))

	// User endpoints
	api.HandleFunc("/me", handlers.GetCurrentUser).Methods("GET")

	// Organization endpoints
	api.HandleFunc("/orgs/{id}/members", handlers.GetOrgMembers).Methods("GET")
	api.HandleFunc("/orgs/{id}/members", middleware.RequireRole("admin")(handlers.AddOrgMember)).Methods("POST")
	api.HandleFunc("/orgs/{id}/members/{userId}", middleware.RequireRole("admin")(handlers.RemoveOrgMember)).Methods("DELETE")

	// Review endpoints with RBAC
	api.HandleFunc("/reviews", handlers.ListReviews).Methods("GET")
	api.HandleFunc("/reviews", middleware.RequireRole("reviewer", "admin")(handlers.CreateReview)).Methods("POST")
	api.HandleFunc("/reviews/{id}", handlers.GetReview).Methods("GET")
	api.HandleFunc("/reviews/{id}", middleware.RequireRole("reviewer", "admin")(handlers.UpdateReview)).Methods("PUT")
	api.HandleFunc("/reviews/{id}/approve", middleware.RequireRole("admin")(handlers.ApproveReview)).Methods("POST")

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Server starting on port %s", port)
	if err := http.ListenAndServe(":"+port, r); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
