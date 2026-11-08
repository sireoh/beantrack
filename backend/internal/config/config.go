// Package config loads BeanTrack's settings from environment variables.
package config

import (
	"encoding/base64"
	"errors"
	"fmt"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

const (
	// DBFileName is the SQLite file inside DATA_DIR. Litestream's config points
	// at the same name, so keep the two in sync.
	DBFileName = "beantrack.db"

	DefaultDiscordAPIBaseURL   = "https://discord.com/api/v10"
	DefaultDiscordAuthorizeURL = "https://discord.com/oauth2/authorize"
	DefaultSessionTTL          = 30 * 24 * time.Hour
	DefaultLoginRedirectURL    = "/"

	// MinSessionSecretLen is the shortest SESSION_SECRET accepted.
	MinSessionSecretLen = 32
)

// requiredVars must be set for the app to start.
var requiredVars = []string{
	"PORT",
	"DATA_DIR",
	"DISCORD_CLIENT_ID",
	"DISCORD_CLIENT_SECRET",
	"DISCORD_REDIRECT_URI",
	"SESSION_SECRET",
}

// backupVars are read by Litestream, not by the app. They are checked as a
// group: either none are set (backups off, e.g. local development) or all of
// them are. A partial set is a startup error, because Litestream silently
// uploads an *unencrypted* replica when LITESTREAM_ENCRYPTION_KEY expands to "".
var backupVars = []string{
	"B2_BUCKET",
	"B2_ENDPOINT",
	"B2_REGION",
	"B2_KEY_ID",
	"B2_APPLICATION_KEY",
	"LITESTREAM_ENCRYPTION_KEY",
}

// Config holds all runtime settings.
type Config struct {
	Port    string
	DataDir string

	DiscordClientID     string
	DiscordClientSecret string
	DiscordRedirectURI  string

	SessionSecret string
	SessionTTL    time.Duration

	// LoginRedirectURL is where the browser is sent after a successful login.
	// Optional (LOGIN_REDIRECT_URL); defaults to "/".
	LoginRedirectURL string

	// BackupsConfigured reports whether the B2/Litestream variables are set.
	BackupsConfigured bool

	// Discord endpoints. Not read from the environment; tests point them at a
	// mock server.
	DiscordAPIBaseURL   string
	DiscordAuthorizeURL string
}

// DBPath is the full path of the SQLite database file.
func (c *Config) DBPath() string {
	return filepath.Join(c.DataDir, DBFileName)
}

// ListenAddr is the address the HTTP server binds to.
func (c *Config) ListenAddr() string {
	return "0.0.0.0:" + c.Port
}

// Load reads the configuration from the process environment.
func Load() (*Config, error) {
	return FromLookup(os.LookupEnv)
}

// FromLookup builds a Config using lookup (os.LookupEnv in production). It
// reports every missing or invalid variable in one error.
func FromLookup(lookup func(string) (string, bool)) (*Config, error) {
	get := func(key string) string {
		v, _ := lookup(key)
		return strings.TrimSpace(v)
	}

	var missing []string
	for _, key := range requiredVars {
		if get(key) == "" {
			missing = append(missing, key)
		}
	}
	if len(missing) > 0 {
		return nil, fmt.Errorf("missing required environment variables: %s", strings.Join(missing, ", "))
	}

	cfg := &Config{
		Port:                get("PORT"),
		DataDir:             get("DATA_DIR"),
		DiscordClientID:     get("DISCORD_CLIENT_ID"),
		DiscordClientSecret: get("DISCORD_CLIENT_SECRET"),
		DiscordRedirectURI:  get("DISCORD_REDIRECT_URI"),
		SessionSecret:       get("SESSION_SECRET"),
		SessionTTL:          DefaultSessionTTL,
		LoginRedirectURL:    get("LOGIN_REDIRECT_URL"),
		DiscordAPIBaseURL:   DefaultDiscordAPIBaseURL,
		DiscordAuthorizeURL: DefaultDiscordAuthorizeURL,
	}
	if cfg.LoginRedirectURL == "" {
		cfg.LoginRedirectURL = DefaultLoginRedirectURL
	}

	var problems []string

	if n, err := strconv.Atoi(cfg.Port); err != nil || n < 1 || n > 65535 {
		problems = append(problems, fmt.Sprintf("PORT must be a number between 1 and 65535 (got %q)", cfg.Port))
	}
	if len(cfg.SessionSecret) < MinSessionSecretLen {
		problems = append(problems, fmt.Sprintf("SESSION_SECRET must be at least %d characters", MinSessionSecretLen))
	}
	if u, err := url.Parse(cfg.DiscordRedirectURI); err != nil || (u.Scheme != "http" && u.Scheme != "https") || u.Host == "" {
		problems = append(problems, "DISCORD_REDIRECT_URI must be an absolute http(s) URL")
	}

	var setBackup, unsetBackup []string
	for _, key := range backupVars {
		if get(key) == "" {
			unsetBackup = append(unsetBackup, key)
		} else {
			setBackup = append(setBackup, key)
		}
	}
	switch {
	case len(setBackup) == 0:
		cfg.BackupsConfigured = false
	case len(unsetBackup) > 0:
		problems = append(problems, fmt.Sprintf(
			"backup settings are partially configured; also set: %s (or unset all of %s)",
			strings.Join(unsetBackup, ", "), strings.Join(backupVars, ", ")))
	default:
		cfg.BackupsConfigured = true
		if err := validateEncryptionKey(get("LITESTREAM_ENCRYPTION_KEY")); err != nil {
			problems = append(problems, err.Error())
		}
	}

	if len(problems) > 0 {
		return nil, errors.New("invalid configuration: " + strings.Join(problems, "; "))
	}
	return cfg, nil
}

// validateEncryptionKey checks that the key is what Litestream's SSE-C setting
// expects: base64 of exactly 32 bytes (AES-256).
func validateEncryptionKey(key string) error {
	raw, err := base64.StdEncoding.DecodeString(key)
	if err != nil || len(raw) != 32 {
		return errors.New("LITESTREAM_ENCRYPTION_KEY must be a base64-encoded 32-byte key (generate one with: openssl rand -base64 32)")
	}
	return nil
}
