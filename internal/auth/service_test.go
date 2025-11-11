package auth

import (
	"testing"
	"time"

	"github.com/andres20980/aurea-orchestrator/internal/models"
)

func TestGenerateToken(t *testing.T) {
	service := NewService("test-secret", 24*time.Hour)

	user := models.User{
		ID:       "1",
		Username: "testuser",
		Email:    "test@example.com",
		Role:     models.RoleAdmin,
		OrgID:    "org1",
	}

	token, err := service.GenerateToken(user)
	if err != nil {
		t.Fatalf("Failed to generate token: %v", err)
	}

	if token == "" {
		t.Error("Generated token is empty")
	}
}

func TestValidateToken(t *testing.T) {
	service := NewService("test-secret", 24*time.Hour)

	user := models.User{
		ID:       "1",
		Username: "testuser",
		Email:    "test@example.com",
		Role:     models.RoleAdmin,
		OrgID:    "org1",
	}

	token, err := service.GenerateToken(user)
	if err != nil {
		t.Fatalf("Failed to generate token: %v", err)
	}

	claims, err := service.ValidateToken(token)
	if err != nil {
		t.Fatalf("Failed to validate token: %v", err)
	}

	if claims.UserID != user.ID {
		t.Errorf("Expected UserID %s, got %s", user.ID, claims.UserID)
	}
	if claims.Username != user.Username {
		t.Errorf("Expected Username %s, got %s", user.Username, claims.Username)
	}
	if claims.Role != user.Role {
		t.Errorf("Expected Role %s, got %s", user.Role, claims.Role)
	}
	if claims.OrgID != user.OrgID {
		t.Errorf("Expected OrgID %s, got %s", user.OrgID, claims.OrgID)
	}
}

func TestValidateTokenWithInvalidSecret(t *testing.T) {
	service := NewService("test-secret", 24*time.Hour)
	user := models.User{
		ID:       "1",
		Username: "testuser",
		Email:    "test@example.com",
		Role:     models.RoleAdmin,
		OrgID:    "org1",
	}

	token, _ := service.GenerateToken(user)

	// Try to validate with different secret
	wrongService := NewService("wrong-secret", 24*time.Hour)
	_, err := wrongService.ValidateToken(token)

	if err == nil {
		t.Error("Expected error when validating with wrong secret")
	}
}

func TestValidateExpiredToken(t *testing.T) {
	// Create service with very short TTL
	service := NewService("test-secret", 1*time.Nanosecond)

	user := models.User{
		ID:       "1",
		Username: "testuser",
		Email:    "test@example.com",
		Role:     models.RoleAdmin,
		OrgID:    "org1",
	}

	token, err := service.GenerateToken(user)
	if err != nil {
		t.Fatalf("Failed to generate token: %v", err)
	}

	// Wait for token to expire
	time.Sleep(10 * time.Millisecond)

	// Now create a new service for validation
	validateService := NewService("test-secret", 24*time.Hour)
	_, err = validateService.ValidateToken(token)

	if err == nil {
		t.Error("Expected error for expired token")
	}
}

func TestAuthenticate(t *testing.T) {
	service := NewService("test-secret", 24*time.Hour)

	tests := []struct {
		username    string
		password    string
		expectError bool
	}{
		{"admin", "password", false},
		{"reviewer", "password", false},
		{"dev", "password", false},
		{"admin", "wrongpassword", true},
		{"nonexistent", "password", true},
	}

	for _, tt := range tests {
		user, err := service.Authenticate(tt.username, tt.password)

		if tt.expectError {
			if err == nil {
				t.Errorf("Expected error for username=%s, password=%s", tt.username, tt.password)
			}
		} else {
			if err != nil {
				t.Errorf("Unexpected error for username=%s: %v", tt.username, err)
			}
			if user == nil {
				t.Errorf("Expected user for username=%s", tt.username)
			}
			if user != nil && user.Username != tt.username {
				t.Errorf("Expected username %s, got %s", tt.username, user.Username)
			}
		}
	}
}
