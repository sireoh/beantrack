// Command server runs the BeanTrack HTTP API.
package main

import (
	"context"
	"errors"
	"fmt"
	"io/fs"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/joho/godotenv"

	"github.com/beantrack/backend/internal/config"
	"github.com/beantrack/backend/internal/db"
	"github.com/beantrack/backend/internal/server"
)

const shutdownTimeout = 15 * time.Second

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	if err := run(logger); err != nil {
		logger.Error("server stopped with error", "err", err)
		os.Exit(1)
	}
}

func run(logger *slog.Logger) error {
	// .env is optional and never overrides variables already set, so the
	// real environment (e.g. a container's) always wins.
	if err := godotenv.Load(); err != nil && !errors.Is(err, fs.ErrNotExist) {
		return fmt.Errorf("loading .env: %w", err)
	}

	cfg, err := config.Load()
	if err != nil {
		return err
	}
	if !cfg.BackupsConfigured {
		logger.Warn("B2/Litestream variables are not set; backups are not configured")
	}

	database, err := db.Open(cfg.DataDir)
	if err != nil {
		return err
	}
	defer func() {
		if err := db.Close(database); err != nil {
			logger.Error("closing database", "err", err)
		} else {
			logger.Info("database closed")
		}
	}()

	e, err := server.New(cfg, database, server.Options{Logger: logger})
	if err != nil {
		return err
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	errCh := make(chan error, 1)
	go func() {
		logger.Info("listening", "addr", cfg.ListenAddr(), "db", cfg.DBPath())
		errCh <- e.Start(cfg.ListenAddr())
	}()

	select {
	case err := <-errCh:
		if !errors.Is(err, http.ErrServerClosed) {
			return fmt.Errorf("http server: %w", err)
		}
		return nil
	case <-ctx.Done():
	}

	logger.Info("shutting down")
	shutdownCtx, cancel := context.WithTimeout(context.Background(), shutdownTimeout)
	defer cancel()
	if err := e.Shutdown(shutdownCtx); err != nil {
		return fmt.Errorf("graceful shutdown: %w", err)
	}
	return nil
}
