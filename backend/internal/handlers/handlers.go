// Package handlers holds the JSON API handlers.
package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"

	"github.com/beantrack/backend/internal/auth"
	"github.com/beantrack/backend/internal/models"
)

// MeResponse is the body of GET /api/me.
type MeResponse struct {
	ID          uint      `json:"id"`
	DiscordID   string    `json:"discord_id"`
	Username    string    `json:"username"`
	GlobalName  *string   `json:"global_name"`
	AvatarURL   string    `json:"avatar_url"`
	Email       *string   `json:"email"`
	TVListID    uint      `json:"tv_list_id"`
	MovieListID uint      `json:"movie_list_id"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// Handlers groups handlers that need the database.
type Handlers struct {
	DB *gorm.DB
}

// Me returns the signed-in user's profile and list IDs.
func (h *Handlers) Me(c echo.Context) error {
	current := auth.CurrentUser(c)
	if current == nil {
		return echo.NewHTTPError(http.StatusUnauthorized, "authentication required")
	}
	var u models.User
	if err := h.DB.WithContext(c.Request().Context()).
		Preload("TVList").Preload("MovieList").
		Take(&u, current.ID).Error; err != nil {
		return err
	}
	resp := MeResponse{
		ID:         u.ID,
		DiscordID:  u.DiscordID,
		Username:   u.Username,
		GlobalName: u.GlobalName,
		AvatarURL:  u.AvatarURL,
		Email:      u.Email,
		CreatedAt:  u.CreatedAt,
		UpdatedAt:  u.UpdatedAt,
	}
	if u.TVList != nil {
		resp.TVListID = u.TVList.ID
	}
	if u.MovieList != nil {
		resp.MovieListID = u.MovieList.ID
	}
	return c.JSON(http.StatusOK, resp)
}

// Healthz reports whether the server can reach its database.
func (h *Handlers) Healthz(c echo.Context) error {
	ctx, cancel := context.WithTimeout(c.Request().Context(), 2*time.Second)
	defer cancel()
	sqlDB, err := h.DB.DB()
	if err == nil {
		err = sqlDB.PingContext(ctx)
	}
	if err != nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"status": "unavailable"})
	}
	return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
}
