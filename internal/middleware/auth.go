package middleware

import (
	"context"
	"net/http"
	"strings"

	"github.com/andres20980/aurea-orchestrator/internal/auth"
	"github.com/andres20980/aurea-orchestrator/internal/models"
)

type contextKey string

const UserContextKey contextKey = "user"

// JWTAuth middleware validates JWT tokens
func JWTAuth(secret string) func(http.Handler) http.Handler {
	authService := auth.NewService(secret, 0) // TTL not needed for validation

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				http.Error(w, "Authorization header required", http.StatusUnauthorized)
				return
			}

			// Expected format: "Bearer <token>"
			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || parts[0] != "Bearer" {
				http.Error(w, "Invalid authorization header format", http.StatusUnauthorized)
				return
			}

			token := parts[1]
			claims, err := authService.ValidateToken(token)
			if err != nil {
				http.Error(w, "Invalid or expired token", http.StatusUnauthorized)
				return
			}

			// Add user info to context
			user := models.User{
				ID:       claims.UserID,
				Username: claims.Username,
				Email:    claims.Email,
				Role:     claims.Role,
				OrgID:    claims.OrgID,
			}

			ctx := context.WithValue(r.Context(), UserContextKey, user)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// RequireRole middleware checks if user has one of the required roles
func RequireRole(roles ...string) func(http.HandlerFunc) http.HandlerFunc {
	return func(next http.HandlerFunc) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {
			user, ok := r.Context().Value(UserContextKey).(models.User)
			if !ok {
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}

			// Check if user has any of the required roles
			hasRole := false
			for _, role := range roles {
				if string(user.Role) == role {
					hasRole = true
					break
				}
			}

			if !hasRole {
				http.Error(w, "Forbidden: insufficient permissions", http.StatusForbidden)
				return
			}

			next(w, r)
		}
	}
}

// GetUserFromContext retrieves the user from request context
func GetUserFromContext(ctx context.Context) (models.User, bool) {
	user, ok := ctx.Value(UserContextKey).(models.User)
	return user, ok
}
