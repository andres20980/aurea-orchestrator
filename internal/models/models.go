package models

// Role represents user role in the system
type Role string

const (
	RoleAdmin    Role = "admin"
	RoleReviewer Role = "reviewer"
	RoleDev      Role = "dev"
)

// User represents a user in the system
type User struct {
	ID       string   `json:"id"`
	Username string   `json:"username"`
	Email    string   `json:"email"`
	Role     Role     `json:"role"`
	OrgID    string   `json:"org_id"`
	OrgName  string   `json:"org_name,omitempty"`
}

// Organization represents an organization/tenant
type Organization struct {
	ID      string   `json:"id"`
	Name    string   `json:"name"`
	Members []string `json:"members"`
}

// Review represents a review item
type Review struct {
	ID       string `json:"id"`
	Title    string `json:"title"`
	Content  string `json:"content"`
	Status   string `json:"status"`
	OrgID    string `json:"org_id"`
	AuthorID string `json:"author_id"`
	Approved bool   `json:"approved"`
}

// LoginRequest represents login credentials
type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// LoginResponse represents login response with JWT token
type LoginResponse struct {
	Token string `json:"token"`
	User  User   `json:"user"`
}
