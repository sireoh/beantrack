// Package models holds the GORM models for BeanTrack.
package models

import "time"

// User is a person who signed in with Discord.
type User struct {
	ID         uint    `gorm:"primaryKey"`
	DiscordID  string  `gorm:"uniqueIndex;not null"`
	Username   string  `gorm:"not null"`
	GlobalName *string // Discord display name; may be unset
	AvatarURL  string  `gorm:"not null;default:''"`
	Email      *string // only present if the email scope was granted
	CreatedAt  time.Time
	UpdatedAt  time.Time

	TVList    *TVList    `gorm:"constraint:OnDelete:CASCADE"`
	MovieList *MovieList `gorm:"constraint:OnDelete:CASCADE"`
}

// Session is a signed-in browser session. Only a SHA-256 hash of the session
// token is stored; the raw token lives only in the user's cookie. The Discord
// tokens are encrypted with a key derived from SESSION_SECRET.
type Session struct {
	ID        uint   `gorm:"primaryKey"`
	UserID    uint   `gorm:"not null;index"`
	User      User   `gorm:"constraint:OnDelete:CASCADE"`
	TokenHash string `gorm:"uniqueIndex;not null;size:64"`

	DiscordAccessToken  string `gorm:"not null"`
	DiscordRefreshToken string `gorm:"not null;default:''"`
	TokenExpiry         time.Time

	// ExpiresAt is when this BeanTrack session stops being valid.
	ExpiresAt time.Time `gorm:"not null;index"`
	CreatedAt time.Time
}

// TVList is a user's single TV list.
type TVList struct {
	ID        uint `gorm:"primaryKey"`
	UserID    uint `gorm:"uniqueIndex;not null"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

func (TVList) TableName() string { return "tv_lists" }

// MovieList is a user's single movie list.
type MovieList struct {
	ID        uint `gorm:"primaryKey"`
	UserID    uint `gorm:"uniqueIndex;not null"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

func (MovieList) TableName() string { return "movie_lists" }

// All lists every model, in migration order.
func All() []any {
	return []any{&User{}, &Session{}, &TVList{}, &MovieList{}}
}
