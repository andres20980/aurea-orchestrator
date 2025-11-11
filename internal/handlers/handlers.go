package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/andres20980/aurea-orchestrator/internal/auth"
	"github.com/andres20980/aurea-orchestrator/internal/middleware"
	"github.com/andres20980/aurea-orchestrator/internal/models"
	"github.com/gorilla/mux"
)

// Mock data store (in production, use a real database)
var (
	orgs = map[string]models.Organization{
		"org1": {
			ID:      "org1",
			Name:    "Organization 1",
			Members: []string{"1", "2"},
		},
		"org2": {
			ID:      "org2",
			Name:    "Organization 2",
			Members: []string{"3"},
		},
	}
	
	reviews = map[string]models.Review{
		"review1": {
			ID:       "review1",
			Title:    "Code Review",
			Content:  "Review the authentication module",
			Status:   "pending",
			OrgID:    "org1",
			AuthorID: "2",
			Approved: false,
		},
	}
)

// Login handles user authentication
func Login(authService *auth.Service) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req models.LoginRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		user, err := authService.Authenticate(req.Username, req.Password)
		if err != nil {
			http.Error(w, "Invalid credentials", http.StatusUnauthorized)
			return
		}

		token, err := authService.GenerateToken(*user)
		if err != nil {
			http.Error(w, "Failed to generate token", http.StatusInternalServerError)
			return
		}

		response := models.LoginResponse{
			Token: token,
			User:  *user,
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}
}

// GetCurrentUser returns the current authenticated user
func GetCurrentUser(w http.ResponseWriter, r *http.Request) {
	user, ok := middleware.GetUserFromContext(r.Context())
	if !ok {
		http.Error(w, "User not found in context", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// GetOrgMembers returns members of an organization
func GetOrgMembers(w http.ResponseWriter, r *http.Request) {
	user, ok := middleware.GetUserFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	vars := mux.Vars(r)
	orgID := vars["id"]

	// Check if user belongs to the organization
	if user.OrgID != orgID {
		http.Error(w, "Forbidden: cannot access other organization's members", http.StatusForbidden)
		return
	}

	org, exists := orgs[orgID]
	if !exists {
		http.Error(w, "Organization not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(org)
}

// AddOrgMember adds a member to an organization (admin only)
func AddOrgMember(w http.ResponseWriter, r *http.Request) {
	user, ok := middleware.GetUserFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	vars := mux.Vars(r)
	orgID := vars["id"]

	// Check if user belongs to the organization
	if user.OrgID != orgID {
		http.Error(w, "Forbidden: cannot modify other organization's members", http.StatusForbidden)
		return
	}

	var req struct {
		UserID string `json:"user_id"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	org, exists := orgs[orgID]
	if !exists {
		http.Error(w, "Organization not found", http.StatusNotFound)
		return
	}

	org.Members = append(org.Members, req.UserID)
	orgs[orgID] = org

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(org)
}

// RemoveOrgMember removes a member from an organization (admin only)
func RemoveOrgMember(w http.ResponseWriter, r *http.Request) {
	user, ok := middleware.GetUserFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	vars := mux.Vars(r)
	orgID := vars["id"]
	userID := vars["userId"]

	// Check if user belongs to the organization
	if user.OrgID != orgID {
		http.Error(w, "Forbidden: cannot modify other organization's members", http.StatusForbidden)
		return
	}

	org, exists := orgs[orgID]
	if !exists {
		http.Error(w, "Organization not found", http.StatusNotFound)
		return
	}

	// Remove member
	newMembers := []string{}
	for _, m := range org.Members {
		if m != userID {
			newMembers = append(newMembers, m)
		}
	}
	org.Members = newMembers
	orgs[orgID] = org

	w.WriteHeader(http.StatusNoContent)
}

// ListReviews returns all reviews for the user's organization
func ListReviews(w http.ResponseWriter, r *http.Request) {
	user, ok := middleware.GetUserFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	// Filter reviews by organization
	var orgReviews []models.Review
	for _, review := range reviews {
		if review.OrgID == user.OrgID {
			orgReviews = append(orgReviews, review)
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(orgReviews)
}

// GetReview returns a specific review
func GetReview(w http.ResponseWriter, r *http.Request) {
	user, ok := middleware.GetUserFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	vars := mux.Vars(r)
	reviewID := vars["id"]

	review, exists := reviews[reviewID]
	if !exists {
		http.Error(w, "Review not found", http.StatusNotFound)
		return
	}

	// Check if user belongs to the same organization
	if review.OrgID != user.OrgID {
		http.Error(w, "Forbidden: cannot access other organization's reviews", http.StatusForbidden)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(review)
}

// CreateReview creates a new review (reviewer/admin only)
func CreateReview(w http.ResponseWriter, r *http.Request) {
	user, ok := middleware.GetUserFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	var req struct {
		Title   string `json:"title"`
		Content string `json:"content"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	reviewID := "review" + string(rune(len(reviews)+1+'0'))
	review := models.Review{
		ID:       reviewID,
		Title:    req.Title,
		Content:  req.Content,
		Status:   "pending",
		OrgID:    user.OrgID,
		AuthorID: user.ID,
		Approved: false,
	}

	reviews[reviewID] = review

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(review)
}

// UpdateReview updates an existing review (reviewer/admin only)
func UpdateReview(w http.ResponseWriter, r *http.Request) {
	user, ok := middleware.GetUserFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	vars := mux.Vars(r)
	reviewID := vars["id"]

	review, exists := reviews[reviewID]
	if !exists {
		http.Error(w, "Review not found", http.StatusNotFound)
		return
	}

	// Check if user belongs to the same organization
	if review.OrgID != user.OrgID {
		http.Error(w, "Forbidden: cannot modify other organization's reviews", http.StatusForbidden)
		return
	}

	var req struct {
		Title   string `json:"title"`
		Content string `json:"content"`
		Status  string `json:"status"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if req.Title != "" {
		review.Title = req.Title
	}
	if req.Content != "" {
		review.Content = req.Content
	}
	if req.Status != "" {
		review.Status = req.Status
	}

	reviews[reviewID] = review

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(review)
}

// ApproveReview approves a review (admin only)
func ApproveReview(w http.ResponseWriter, r *http.Request) {
	user, ok := middleware.GetUserFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	vars := mux.Vars(r)
	reviewID := vars["id"]

	review, exists := reviews[reviewID]
	if !exists {
		http.Error(w, "Review not found", http.StatusNotFound)
		return
	}

	// Check if user belongs to the same organization
	if review.OrgID != user.OrgID {
		http.Error(w, "Forbidden: cannot approve other organization's reviews", http.StatusForbidden)
		return
	}

	review.Approved = true
	review.Status = "approved"
	reviews[reviewID] = review

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(review)
}
