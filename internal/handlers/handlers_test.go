package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/andres20980/aurea-orchestrator/internal/auth"
	"github.com/andres20980/aurea-orchestrator/internal/middleware"
	"github.com/andres20980/aurea-orchestrator/internal/models"
	"github.com/gorilla/mux"
)

func setupTestRouter(secret string) *mux.Router {
	authService := auth.NewService(secret, 24*time.Hour)
	r := mux.NewRouter()

	// Public endpoints
	r.HandleFunc("/login", Login(authService)).Methods("POST")

	// Protected endpoints
	api := r.PathPrefix("/api").Subrouter()
	api.Use(middleware.JWTAuth(secret))

	api.HandleFunc("/me", GetCurrentUser).Methods("GET")
	api.HandleFunc("/orgs/{id}/members", GetOrgMembers).Methods("GET")
	api.HandleFunc("/reviews", ListReviews).Methods("GET")
	api.HandleFunc("/reviews/{id}", GetReview).Methods("GET")
	api.HandleFunc("/reviews", middleware.RequireRole("reviewer", "admin")(CreateReview)).Methods("POST")
	api.HandleFunc("/reviews/{id}/approve", middleware.RequireRole("admin")(ApproveReview)).Methods("POST")

	return r
}

func TestLogin(t *testing.T) {
	router := setupTestRouter("test-secret")

	tests := []struct {
		name           string
		username       string
		password       string
		expectedStatus int
	}{
		{"Valid admin login", "admin", "password", http.StatusOK},
		{"Valid reviewer login", "reviewer", "password", http.StatusOK},
		{"Valid dev login", "dev", "password", http.StatusOK},
		{"Invalid password", "admin", "wrongpassword", http.StatusUnauthorized},
		{"Invalid username", "nonexistent", "password", http.StatusUnauthorized},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			reqBody := models.LoginRequest{
				Username: tt.username,
				Password: tt.password,
			}
			body, _ := json.Marshal(reqBody)

			req := httptest.NewRequest("POST", "/login", bytes.NewBuffer(body))
			req.Header.Set("Content-Type", "application/json")
			rr := httptest.NewRecorder()

			router.ServeHTTP(rr, req)

			if rr.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, rr.Code)
			}

			if tt.expectedStatus == http.StatusOK {
				var response models.LoginResponse
				if err := json.NewDecoder(rr.Body).Decode(&response); err != nil {
					t.Fatalf("Failed to decode response: %v", err)
				}

				if response.Token == "" {
					t.Error("Expected token in response")
				}
				if response.User.Username != tt.username {
					t.Errorf("Expected username %s, got %s", tt.username, response.User.Username)
				}
			}
		})
	}
}

func TestGetCurrentUser(t *testing.T) {
	router := setupTestRouter("test-secret")
	authService := auth.NewService("test-secret", 24*time.Hour)

	user := models.User{
		ID:       "1",
		Username: "admin",
		Email:    "admin@example.com",
		Role:     models.RoleAdmin,
		OrgID:    "org1",
	}

	token, _ := authService.GenerateToken(user)

	req := httptest.NewRequest("GET", "/api/me", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	rr := httptest.NewRecorder()

	router.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, rr.Code)
	}

	var responseUser models.User
	if err := json.NewDecoder(rr.Body).Decode(&responseUser); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	if responseUser.Username != user.Username {
		t.Errorf("Expected username %s, got %s", user.Username, responseUser.Username)
	}
}

func TestGetOrgMembers(t *testing.T) {
	router := setupTestRouter("test-secret")
	authService := auth.NewService("test-secret", 24*time.Hour)

	tests := []struct {
		name           string
		userOrgID      string
		requestOrgID   string
		expectedStatus int
	}{
		{"Access own org", "org1", "org1", http.StatusOK},
		{"Access other org", "org1", "org2", http.StatusForbidden},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			user := models.User{
				ID:       "1",
				Username: "admin",
				Email:    "admin@example.com",
				Role:     models.RoleAdmin,
				OrgID:    tt.userOrgID,
			}

			token, _ := authService.GenerateToken(user)

			req := httptest.NewRequest("GET", "/api/orgs/"+tt.requestOrgID+"/members", nil)
			req.Header.Set("Authorization", "Bearer "+token)
			rr := httptest.NewRecorder()

			router.ServeHTTP(rr, req)

			if rr.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, rr.Code)
			}
		})
	}
}

func TestCreateReviewRBAC(t *testing.T) {
	router := setupTestRouter("test-secret")
	authService := auth.NewService("test-secret", 24*time.Hour)

	tests := []struct {
		name           string
		userRole       models.Role
		expectedStatus int
	}{
		{"Admin can create", models.RoleAdmin, http.StatusCreated},
		{"Reviewer can create", models.RoleReviewer, http.StatusCreated},
		{"Dev cannot create", models.RoleDev, http.StatusForbidden},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			user := models.User{
				ID:       "1",
				Username: "testuser",
				Email:    "test@example.com",
				Role:     tt.userRole,
				OrgID:    "org1",
			}

			token, _ := authService.GenerateToken(user)

			reqBody := map[string]string{
				"title":   "Test Review",
				"content": "Test content",
			}
			body, _ := json.Marshal(reqBody)

			req := httptest.NewRequest("POST", "/api/reviews", bytes.NewBuffer(body))
			req.Header.Set("Authorization", "Bearer "+token)
			req.Header.Set("Content-Type", "application/json")
			rr := httptest.NewRecorder()

			router.ServeHTTP(rr, req)

			if rr.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, rr.Code)
			}
		})
	}
}

func TestApproveReviewRBAC(t *testing.T) {
	router := setupTestRouter("test-secret")
	authService := auth.NewService("test-secret", 24*time.Hour)

	tests := []struct {
		name           string
		userRole       models.Role
		expectedStatus int
	}{
		{"Admin can approve", models.RoleAdmin, http.StatusOK},
		{"Reviewer cannot approve", models.RoleReviewer, http.StatusForbidden},
		{"Dev cannot approve", models.RoleDev, http.StatusForbidden},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			user := models.User{
				ID:       "1",
				Username: "testuser",
				Email:    "test@example.com",
				Role:     tt.userRole,
				OrgID:    "org1",
			}

			token, _ := authService.GenerateToken(user)

			req := httptest.NewRequest("POST", "/api/reviews/review1/approve", nil)
			req.Header.Set("Authorization", "Bearer "+token)
			rr := httptest.NewRecorder()

			router.ServeHTTP(rr, req)

			if rr.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, rr.Code)
			}
		})
	}
}

func TestOrgScopedReviews(t *testing.T) {
	router := setupTestRouter("test-secret")
	authService := auth.NewService("test-secret", 24*time.Hour)

	user := models.User{
		ID:       "1",
		Username: "testuser",
		Email:    "test@example.com",
		Role:     models.RoleAdmin,
		OrgID:    "org1",
	}

	token, _ := authService.GenerateToken(user)

	req := httptest.NewRequest("GET", "/api/reviews", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	rr := httptest.NewRecorder()

	router.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, rr.Code)
	}

	var reviewList []models.Review
	if err := json.NewDecoder(rr.Body).Decode(&reviewList); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	// All reviews should belong to user's org
	for _, review := range reviewList {
		if review.OrgID != user.OrgID {
			t.Errorf("Found review from different org: expected %s, got %s", user.OrgID, review.OrgID)
		}
	}
}
