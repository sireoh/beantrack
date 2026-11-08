// Package apitest holds BeanTrack's API tests. It is not named "testing" so
// it does not clash with the standard library package.
package apitest

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"sync"
	"testing"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"

	"github.com/beantrack/backend/internal/auth"
	"github.com/beantrack/backend/internal/config"
	"github.com/beantrack/backend/internal/db"
	"github.com/beantrack/backend/internal/server"
)

const (
	testClientID     = "test-client-id"
	testClientSecret = "test-client-secret"
	testRedirectURI  = "http://localhost:8080/auth/discord/callback"
	testSecret       = "test-session-secret-that-is-at-least-32-chars"
)

// mockDiscord is a fake Discord API. Each auth code maps to a profile; the
// token endpoint issues an access token for the code and /users/@me returns
// that profile.
type mockDiscord struct {
	t      *testing.T
	server *httptest.Server

	mu           sync.Mutex
	profiles     map[string]map[string]any // code -> profile JSON
	tokens       map[string]string         // access token -> code
	tokenCalls   int
	profileCalls int
}

func newMockDiscord(t *testing.T) *mockDiscord {
	t.Helper()
	m := &mockDiscord{
		t:        t,
		profiles: map[string]map[string]any{},
		tokens:   map[string]string{},
	}
	mux := http.NewServeMux()
	mux.HandleFunc("POST /oauth2/token", m.handleToken)
	mux.HandleFunc("GET /users/@me", m.handleMe)
	m.server = httptest.NewServer(mux)
	t.Cleanup(m.server.Close)
	return m
}

// expect registers the profile Discord returns for an authorization code.
func (m *mockDiscord) expect(code string, profile map[string]any) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.profiles[code] = profile
}

func (m *mockDiscord) calls() (token, profile int) {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.tokenCalls, m.profileCalls
}

func (m *mockDiscord) handleToken(w http.ResponseWriter, r *http.Request) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.tokenCalls++

	id, secret, ok := r.BasicAuth()
	if !ok || id != testClientID || secret != testClientSecret {
		http.Error(w, `{"error":"invalid_client"}`, http.StatusUnauthorized)
		return
	}
	if err := r.ParseForm(); err != nil {
		http.Error(w, `{"error":"invalid_request"}`, http.StatusBadRequest)
		return
	}
	code := r.PostForm.Get("code")
	if r.PostForm.Get("grant_type") != "authorization_code" ||
		r.PostForm.Get("redirect_uri") != testRedirectURI {
		http.Error(w, `{"error":"invalid_request"}`, http.StatusBadRequest)
		return
	}
	if _, known := m.profiles[code]; !known {
		http.Error(w, `{"error":"invalid_grant"}`, http.StatusBadRequest)
		return
	}
	access := fmt.Sprintf("access-%s-%d", code, m.tokenCalls)
	m.tokens[access] = code
	writeJSON(w, map[string]any{
		"access_token":  access,
		"token_type":    "Bearer",
		"expires_in":    604800,
		"refresh_token": "refresh-" + code,
		"scope":         auth.OAuthScopes,
	})
}

func (m *mockDiscord) handleMe(w http.ResponseWriter, r *http.Request) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.profileCalls++

	token := strings.TrimPrefix(r.Header.Get("Authorization"), "Bearer ")
	code, ok := m.tokens[token]
	if !ok {
		http.Error(w, `{"message":"401: Unauthorized"}`, http.StatusUnauthorized)
		return
	}
	writeJSON(w, m.profiles[code])
}

func writeJSON(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(v)
}

// testApp is a BeanTrack server backed by its own temporary database.
type testApp struct {
	t       *testing.T
	cfg     *config.Config
	db      *gorm.DB
	echo    *echo.Echo
	discord *mockDiscord
}

func newTestApp(t *testing.T) *testApp {
	t.Helper()
	discord := newMockDiscord(t)

	cfg := &config.Config{
		Port:                "0",
		DataDir:             t.TempDir() + "/data", // a missing dir, to check it gets created
		DiscordClientID:     testClientID,
		DiscordClientSecret: testClientSecret,
		DiscordRedirectURI:  testRedirectURI,
		SessionSecret:       testSecret,
		SessionTTL:          config.DefaultSessionTTL,
		LoginRedirectURL:    "/app",
		DiscordAPIBaseURL:   discord.server.URL,
		DiscordAuthorizeURL: discord.server.URL + "/oauth2/authorize",
	}

	gdb, err := db.Open(cfg.DataDir)
	if err != nil {
		t.Fatalf("opening db: %v", err)
	}
	// Registered after t.TempDir, so it runs first: Windows cannot delete an
	// open database file.
	t.Cleanup(func() { _ = db.Close(gdb) })

	e, err := server.New(cfg, gdb, server.Options{HTTPClient: discord.server.Client()})
	if err != nil {
		t.Fatalf("building server: %v", err)
	}
	return &testApp{t: t, cfg: cfg, db: gdb, echo: e, discord: discord}
}

// do sends a request through the app and returns the recorded response.
func (a *testApp) do(method, target string, cookies ...*http.Cookie) *httptest.ResponseRecorder {
	a.t.Helper()
	req := httptest.NewRequest(method, target, nil)
	for _, c := range cookies {
		if c != nil {
			req.AddCookie(c)
		}
	}
	rec := httptest.NewRecorder()
	a.echo.ServeHTTP(rec, req)
	return rec
}

// startLogin hits /auth/discord/login and returns the state from the
// redirect URL plus the state cookie.
func (a *testApp) startLogin() (string, *http.Cookie) {
	a.t.Helper()
	rec := a.do(http.MethodGet, "/auth/discord/login")
	if rec.Code != http.StatusFound {
		a.t.Fatalf("login: status %d, want 302", rec.Code)
	}
	loc, err := url.Parse(rec.Header().Get("Location"))
	if err != nil {
		a.t.Fatalf("login: bad Location: %v", err)
	}
	state := loc.Query().Get("state")
	if state == "" {
		a.t.Fatal("login: redirect has no state")
	}
	return state, findCookie(a.t, rec, auth.StateCookieName)
}

// login runs the whole OAuth flow for code and returns the session cookie.
func (a *testApp) login(code string) *http.Cookie {
	a.t.Helper()
	state, stateCookie := a.startLogin()
	rec := a.do(http.MethodGet, "/auth/discord/callback?code="+url.QueryEscape(code)+"&state="+url.QueryEscape(state), stateCookie)
	if rec.Code != http.StatusSeeOther {
		a.t.Fatalf("callback: status %d, want 303; body: %s", rec.Code, rec.Body.String())
	}
	if got := rec.Header().Get("Location"); got != a.cfg.LoginRedirectURL {
		a.t.Fatalf("callback redirected to %q, want %q", got, a.cfg.LoginRedirectURL)
	}
	return findCookie(a.t, rec, auth.SessionCookieName)
}

// me calls GET /api/me and decodes the response.
func (a *testApp) me(session *http.Cookie) map[string]any {
	a.t.Helper()
	rec := a.do(http.MethodGet, "/api/me", session)
	if rec.Code != http.StatusOK {
		a.t.Fatalf("/api/me: status %d, want 200; body: %s", rec.Code, rec.Body.String())
	}
	var body map[string]any
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil {
		a.t.Fatalf("/api/me: decoding body: %v", err)
	}
	return body
}

func (a *testApp) count(model any) int64 {
	a.t.Helper()
	var n int64
	if err := a.db.Model(model).Count(&n).Error; err != nil {
		a.t.Fatalf("counting: %v", err)
	}
	return n
}

func findCookie(t *testing.T, rec *httptest.ResponseRecorder, name string) *http.Cookie {
	t.Helper()
	for _, c := range rec.Result().Cookies() {
		if c.Name == name {
			return c
		}
	}
	t.Fatalf("response has no %q cookie", name)
	return nil
}

func profile(id, username, globalName, avatar string) map[string]any {
	p := map[string]any{
		"id":            id,
		"username":      username,
		"discriminator": "0",
		"global_name":   nil,
		"avatar":        nil,
		"email":         username + "@example.com",
	}
	if globalName != "" {
		p["global_name"] = globalName
	}
	if avatar != "" {
		p["avatar"] = avatar
	}
	return p
}
