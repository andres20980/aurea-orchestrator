package auth

import (
	"errors"
	"time"

	"github.com/andres20980/aurea-orchestrator/internal/models"
	"github.com/golang-jwt/jwt/v5"
)

var (
	ErrInvalidToken = errors.New("invalid token")
	ErrExpiredToken = errors.New("token has expired")
)

// Claims represents JWT claims with user information
type Claims struct {
	UserID   string      `json:"user_id"`
	Username string      `json:"username"`
	Email    string      `json:"email"`
	Role     models.Role `json:"role"`
	OrgID    string      `json:"org_id"`
	jwt.RegisteredClaims
}

// Service handles authentication operations
type Service struct {
	secret   []byte
	tokenTTL time.Duration
}

// NewService creates a new authentication service
func NewService(secret string, tokenTTL time.Duration) *Service {
	return &Service{
		secret:   []byte(secret),
		tokenTTL: tokenTTL,
	}
}

// GenerateToken creates a new JWT token for a user
func (s *Service) GenerateToken(user models.User) (string, error) {
	claims := Claims{
		UserID:   user.ID,
		Username: user.Username,
		Email:    user.Email,
		Role:     user.Role,
		OrgID:    user.OrgID,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(s.tokenTTL)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(s.secret)
}

// ValidateToken validates a JWT token and returns the claims
func (s *Service) ValidateToken(tokenString string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, ErrInvalidToken
		}
		return s.secret, nil
	})

	if err != nil {
		return nil, err
	}

	claims, ok := token.Claims.(*Claims)
	if !ok || !token.Valid {
		return nil, ErrInvalidToken
	}

	return claims, nil
}

// Authenticate validates credentials and returns a user (mock implementation)
func (s *Service) Authenticate(username, password string) (*models.User, error) {
	// This is a mock implementation for demonstration
	// In production, this would validate against a database
	mockUsers := map[string]models.User{
		"admin": {
			ID:       "1",
			Username: "admin",
			Email:    "admin@example.com",
			Role:     models.RoleAdmin,
			OrgID:    "org1",
			OrgName:  "Organization 1",
		},
		"reviewer": {
			ID:       "2",
			Username: "reviewer",
			Email:    "reviewer@example.com",
			Role:     models.RoleReviewer,
			OrgID:    "org1",
			OrgName:  "Organization 1",
		},
		"dev": {
			ID:       "3",
			Username: "dev",
			Email:    "dev@example.com",
			Role:     models.RoleDev,
			OrgID:    "org2",
			OrgName:  "Organization 2",
		},
	}

	user, exists := mockUsers[username]
	if !exists || password != "password" {
		return nil, errors.New("invalid credentials")
	}

	return &user, nil
}
