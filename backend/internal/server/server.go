// Package server wires routes and middleware into an Echo instance.
package server

import (
	"context"
	"log/slog"
	"net/http"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"gorm.io/gorm"

	"github.com/beantrack/backend/internal/auth"
	"github.com/beantrack/backend/internal/config"
	"github.com/beantrack/backend/internal/handlers"
)

// Options tweaks New. The zero value is fine for production.
type Options struct {
	// HTTPClient is used for outbound calls to Discord.
	HTTPClient *http.Client
	Logger     *slog.Logger
}

// New builds the HTTP handler for BeanTrack.
func New(cfg *config.Config, db *gorm.DB, opts Options) (*echo.Echo, error) {
	log := opts.Logger
	if log == nil {
		log = slog.Default()
	}
	httpClient := opts.HTTPClient
	if httpClient == nil {
		httpClient = &http.Client{Timeout: 10 * time.Second}
	}

	authSvc, err := auth.NewService(cfg, db, httpClient, log)
	if err != nil {
		return nil, err
	}
	h := &handlers.Handlers{DB: db}

	e := echo.New()
	e.HideBanner = true
	e.HidePort = true
	e.Server.ReadHeaderTimeout = 10 * time.Second
	e.Server.IdleTimeout = 120 * time.Second

	e.Use(middleware.Recover())
	e.Use(middleware.RequestID())
	e.Use(requestLogger(log))
	e.Use(middleware.Secure())
	e.Use(middleware.BodyLimit("1M"))

	e.GET("/healthz", h.Healthz)

	e.GET("/auth/discord/login", authSvc.Login)
	e.GET("/auth/discord/callback", authSvc.Callback)
	e.POST("/auth/logout", authSvc.Logout)

	api := e.Group("/api", authSvc.RequireSession)
	api.GET("/me", h.Me)

	return e, nil
}

// requestLogger logs one line per request. It logs the path only, never the
// query string, so OAuth codes and state values stay out of the logs.
func requestLogger(log *slog.Logger) echo.MiddlewareFunc {
	return middleware.RequestLoggerWithConfig(middleware.RequestLoggerConfig{
		Skipper:     func(c echo.Context) bool { return c.Path() == "/healthz" },
		LogStatus:   true,
		LogURIPath:  true,
		LogMethod:   true,
		LogLatency:  true,
		LogError:    true,
		LogRemoteIP: true,
		HandleError: true,
		LogValuesFunc: func(c echo.Context, v middleware.RequestLoggerValues) error {
			level := slog.LevelInfo
			attrs := []slog.Attr{
				slog.String("method", v.Method),
				slog.String("path", v.URIPath),
				slog.Int("status", v.Status),
				slog.Duration("latency", v.Latency),
				slog.String("remote_ip", v.RemoteIP),
				slog.String("request_id", c.Response().Header().Get(echo.HeaderXRequestID)),
			}
			if v.Error != nil {
				attrs = append(attrs, slog.String("err", v.Error.Error()))
				if v.Status >= 500 {
					level = slog.LevelError
				}
			}
			log.LogAttrs(context.Background(), level, "request", attrs...)
			return nil
		},
	})
}
