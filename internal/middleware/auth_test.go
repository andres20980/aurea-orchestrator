package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/andres20980/aurea-orchestrator/internal/auth"
	"github.com/andres20980/aurea-orchestrator/internal/models"
)

func TestJWTAuthMiddleware(t *testing.T) {
	secret := "test-secret"
	authService := auth.NewService(secret, 24*time.Hour)

	user := models.User{
		ID:       "1",
		Username: "testuser",
		Email:    "test@example.com",
		Role:     models.RoleAdmin,
		OrgID:    "org1",
	}

	token, _ := authService.GenerateToken(user)

	middleware := JWTAuth(secret)

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		userFromCtx, ok := GetUserFromContext(r.Context())
		if !ok {
			t.Error("User not found in context")
		}
		if userFromCtx.ID != user.ID {
			t.Errorf("Expected user ID %s, got %s", user.ID, userFromCtx.ID)
		}
		w.WriteHeader(http.StatusOK)
	})

	wrappedHandler := middleware(handler)

	tests := []struct {
		name           string
		authHeader     string
		expectedStatus int
	}{
		{
			name:           "Valid token",
			authHeader:     "Bearer " + token,
			expectedStatus: http.StatusOK,
		},
		{
			name:           "Missing auth header",
			authHeader:     "",
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:           "Invalid auth format",
			authHeader:     "InvalidFormat",
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:           "Invalid token",
			authHeader:     "Bearer invalid.token.here",
			expectedStatus: http.StatusUnauthorized,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/test", nil)
			if tt.authHeader != "" {
				req.Header.Set("Authorization", tt.authHeader)
			}
			rr := httptest.NewRecorder()

			wrappedHandler.ServeHTTP(rr, req)

			if rr.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, rr.Code)
			}
		})
	}
}

func TestRequireRoleMiddleware(t *testing.T) {
	secret := "test-secret"
	authService := auth.NewService(secret, 24*time.Hour)

	tests := []struct {
		name           string
		userRole       models.Role
		requiredRoles  []string
		expectedStatus int
	}{
		{
			name:           "Admin accessing admin endpoint",
			userRole:       models.RoleAdmin,
			requiredRoles:  []string{"admin"},
			expectedStatus: http.StatusOK,
		},
		{
			name:           "Reviewer accessing reviewer endpoint",
			userRole:       models.RoleReviewer,
			requiredRoles:  []string{"reviewer", "admin"},
			expectedStatus: http.StatusOK,
		},
		{
			name:           "Dev accessing admin endpoint",
			userRole:       models.RoleDev,
			requiredRoles:  []string{"admin"},
			expectedStatus: http.StatusForbidden,
		},
		{
			name:           "Dev accessing reviewer endpoint",
			userRole:       models.RoleDev,
			requiredRoles:  []string{"reviewer", "admin"},
			expectedStatus: http.StatusForbidden,
		},
		{
			name:           "Admin accessing multi-role endpoint",
			userRole:       models.RoleAdmin,
			requiredRoles:  []string{"reviewer", "admin"},
			expectedStatus: http.StatusOK,
		},
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

			handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
			})

			jwtMiddleware := JWTAuth(secret)
			roleMiddleware := RequireRole(tt.requiredRoles...)
			wrappedHandler := jwtMiddleware(roleMiddleware(handler))

			req := httptest.NewRequest("GET", "/test", nil)
			req.Header.Set("Authorization", "Bearer "+token)
			rr := httptest.NewRecorder()

			wrappedHandler.ServeHTTP(rr, req)

			if rr.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, rr.Code)
			}
		})
	}
}
