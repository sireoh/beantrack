package apitest

import (
	"strings"
	"testing"

	"github.com/beantrack/backend/internal/config"
)

func validEnv() map[string]string {
	return map[string]string{
		"PORT":                  "8080",
		"DATA_DIR":              "/data",
		"DISCORD_CLIENT_ID":     "id",
		"DISCORD_CLIENT_SECRET": "secret",
		"DISCORD_REDIRECT_URI":  "https://beantrack.example/auth/discord/callback",
		"SESSION_SECRET":        strings.Repeat("s", 32),
	}
}

func withBackups(env map[string]string) map[string]string {
	env["B2_BUCKET"] = "bucket"
	env["B2_ENDPOINT"] = "https://s3.us-west-004.backblazeb2.com"
	env["B2_REGION"] = "us-west-004"
	env["B2_KEY_ID"] = "key-id"
	env["B2_APPLICATION_KEY"] = "app-key"
	env["LITESTREAM_ENCRYPTION_KEY"] = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=" // 32 bytes
	return env
}

func load(env map[string]string) (*config.Config, error) {
	return config.FromLookup(func(k string) (string, bool) {
		v, ok := env[k]
		return v, ok
	})
}

func TestConfigLoadsValidEnv(t *testing.T) {
	cfg, err := load(validEnv())
	if err != nil {
		t.Fatal(err)
	}
	if cfg.ListenAddr() != "0.0.0.0:8080" {
		t.Errorf("listen addr %q", cfg.ListenAddr())
	}
	if !strings.HasSuffix(cfg.DBPath(), "beantrack.db") {
		t.Errorf("db path %q", cfg.DBPath())
	}
	if cfg.LoginRedirectURL != "/" || cfg.BackupsConfigured {
		t.Errorf("defaults: %+v", cfg)
	}

	cfg, err = load(withBackups(validEnv()))
	if err != nil {
		t.Fatal(err)
	}
	if !cfg.BackupsConfigured {
		t.Error("BackupsConfigured = false with all backup vars set")
	}
}

func TestConfigReportsAllMissingVars(t *testing.T) {
	_, err := load(map[string]string{"PORT": "8080"})
	if err == nil {
		t.Fatal("expected an error")
	}
	for _, key := range []string{"DATA_DIR", "DISCORD_CLIENT_ID", "DISCORD_CLIENT_SECRET", "DISCORD_REDIRECT_URI", "SESSION_SECRET"} {
		if !strings.Contains(err.Error(), key) {
			t.Errorf("error %q does not mention %s", err, key)
		}
	}
	if strings.Contains(err.Error(), "PORT") {
		t.Errorf("error mentions PORT, which was set: %q", err)
	}
}

func TestConfigRejectsInvalidValues(t *testing.T) {
	cases := map[string]func(map[string]string){
		"bad port":          func(e map[string]string) { e["PORT"] = "eighty" },
		"short secret":      func(e map[string]string) { e["SESSION_SECRET"] = "short" },
		"relative redirect": func(e map[string]string) { e["DISCORD_REDIRECT_URI"] = "/callback" },
		"partial backups": func(e map[string]string) {
			withBackups(e)
			delete(e, "LITESTREAM_ENCRYPTION_KEY")
		},
		"bad encryption key": func(e map[string]string) {
			withBackups(e)
			e["LITESTREAM_ENCRYPTION_KEY"] = "not-32-bytes"
		},
	}
	for name, mutate := range cases {
		t.Run(name, func(t *testing.T) {
			env := validEnv()
			mutate(env)
			if _, err := load(env); err == nil {
				t.Error("expected an error")
			}
		})
	}
}
