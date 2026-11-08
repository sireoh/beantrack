package apitest

import (
	"net/http"
	"net/url"
	"strings"
	"testing"
	"time"

	"github.com/beantrack/backend/internal/auth"
	"github.com/beantrack/backend/internal/models"
)

func TestLoginRedirectsToDiscordWithState(t *testing.T) {
	app := newTestApp(t)

	rec := app.do(http.MethodGet, "/auth/discord/login")
	if rec.Code != http.StatusFound {
		t.Fatalf("status %d, want 302", rec.Code)
	}
	loc, err := url.Parse(rec.Header().Get("Location"))
	if err != nil {
		t.Fatal(err)
	}
	if got, want := loc.Scheme+"://"+loc.Host+loc.Path, app.cfg.DiscordAuthorizeURL; got != want {
		t.Errorf("redirect target %q, want %q", got, want)
	}
	q := loc.Query()
	for key, want := range map[string]string{
		"client_id":     testClientID,
		"redirect_uri":  testRedirectURI,
		"response_type": "code",
		"scope":         auth.OAuthScopes,
	} {
		if got := q.Get(key); got != want {
			t.Errorf("%s = %q, want %q", key, got, want)
		}
	}
	if len(q.Get("state")) < 32 {
		t.Errorf("state %q looks too short", q.Get("state"))
	}

	ck := findCookie(t, rec, auth.StateCookieName)
	if !ck.HttpOnly || !ck.Secure || ck.SameSite != http.SameSiteLaxMode {
		t.Errorf("state cookie flags: HttpOnly=%v Secure=%v SameSite=%v", ck.HttpOnly, ck.Secure, ck.SameSite)
	}

	// Two logins must get different states.
	other := app.do(http.MethodGet, "/auth/discord/login")
	otherLoc, _ := url.Parse(other.Header().Get("Location"))
	if otherLoc.Query().Get("state") == q.Get("state") {
		t.Error("state was reused between login attempts")
	}
}

func TestCallbackCreatesUserAndBothLists(t *testing.T) {
	app := newTestApp(t)
	app.discord.expect("code-1", profile("80351110224678912", "nelly", "Nelly", "8342729096ea3675442027381ff50dfe"))

	session := app.login("code-1")

	if !session.HttpOnly || !session.Secure || session.SameSite != http.SameSiteLaxMode {
		t.Errorf("session cookie flags: HttpOnly=%v Secure=%v SameSite=%v", session.HttpOnly, session.Secure, session.SameSite)
	}
	if session.Path != "/" || session.MaxAge <= 0 {
		t.Errorf("session cookie Path=%q MaxAge=%d", session.Path, session.MaxAge)
	}

	var user models.User
	if err := app.db.Where("discord_id = ?", "80351110224678912").Take(&user).Error; err != nil {
		t.Fatalf("user not created: %v", err)
	}
	if user.Username != "nelly" || user.GlobalName == nil || *user.GlobalName != "Nelly" {
		t.Errorf("user = %+v", user)
	}
	if want := "https://cdn.discordapp.com/avatars/80351110224678912/8342729096ea3675442027381ff50dfe.png"; user.AvatarURL != want {
		t.Errorf("avatar_url = %q, want %q", user.AvatarURL, want)
	}
	if user.Email == nil || *user.Email != "nelly@example.com" {
		t.Errorf("email = %v", user.Email)
	}

	var tv models.TVList
	if err := app.db.Where("user_id = ?", user.ID).Take(&tv).Error; err != nil {
		t.Errorf("tv list not created: %v", err)
	}
	var movies models.MovieList
	if err := app.db.Where("user_id = ?", user.ID).Take(&movies).Error; err != nil {
		t.Errorf("movie list not created: %v", err)
	}
	if n := app.count(&models.Session{}); n != 1 {
		t.Errorf("sessions = %d, want 1", n)
	}
}

func TestRepeatLoginUpdatesUserWithoutDuplicatingLists(t *testing.T) {
	app := newTestApp(t)
	const discordID = "123456789012345678"
	app.discord.expect("first", profile(discordID, "oldname", "Old Name", "oldavatarhash"))
	app.discord.expect("second", profile(discordID, "newname", "New Name", "a_newavatarhash"))

	firstSession := app.login("first")
	before := app.me(firstSession)

	secondSession := app.login("second")
	after := app.me(secondSession)

	if after["username"] != "newname" || after["global_name"] != "New Name" {
		t.Errorf("profile not updated: %v", after)
	}
	if want := "https://cdn.discordapp.com/avatars/" + discordID + "/a_newavatarhash.gif"; after["avatar_url"] != want {
		t.Errorf("avatar_url = %v, want %s", after["avatar_url"], want)
	}
	if before["id"] != after["id"] {
		t.Errorf("user id changed: %v -> %v", before["id"], after["id"])
	}
	if before["tv_list_id"] != after["tv_list_id"] || before["movie_list_id"] != after["movie_list_id"] {
		t.Errorf("list ids changed: before %v/%v, after %v/%v",
			before["tv_list_id"], before["movie_list_id"], after["tv_list_id"], after["movie_list_id"])
	}
	if before["created_at"] != after["created_at"] {
		t.Errorf("created_at changed: %v -> %v", before["created_at"], after["created_at"])
	}

	for name, model := range map[string]any{
		"users":       &models.User{},
		"tv_lists":    &models.TVList{},
		"movie_lists": &models.MovieList{},
	} {
		if n := app.count(model); n != 1 {
			t.Errorf("%s = %d, want 1", name, n)
		}
	}
	// Each login is its own session; the first one stays valid.
	if n := app.count(&models.Session{}); n != 2 {
		t.Errorf("sessions = %d, want 2", n)
	}
	if got := app.me(firstSession)["username"]; got != "newname" {
		t.Errorf("first session sees username %v", got)
	}
}

func TestRepeatLoginWithoutEmailKeepsStoredEmail(t *testing.T) {
	app := newTestApp(t)
	withEmail := profile("42", "sam", "", "")
	withoutEmail := profile("42", "sam", "", "")
	delete(withoutEmail, "email")
	app.discord.expect("a", withEmail)
	app.discord.expect("b", withoutEmail)

	app.login("a")
	got := app.me(app.login("b"))
	if got["email"] != "sam@example.com" {
		t.Errorf("email = %v, want it kept", got["email"])
	}
	if want := "https://cdn.discordapp.com/embed/avatars/0.png"; got["avatar_url"] != want {
		t.Errorf("default avatar = %v, want %s", got["avatar_url"], want)
	}
}

func TestProtectedRoutesRejectRequestsWithoutSession(t *testing.T) {
	app := newTestApp(t)
	app.discord.expect("code", profile("1", "alice", "", ""))
	valid := app.login("code")

	// A token with a valid signature that is not in the database.
	unknown := forgeSignedCookie(t, app, "not-a-real-session")

	cases := map[string]*http.Cookie{
		"no cookie":         nil,
		"empty cookie":      {Name: auth.SessionCookieName, Value: ""},
		"garbage":           {Name: auth.SessionCookieName, Value: "garbage"},
		"tampered":          {Name: auth.SessionCookieName, Value: "x" + valid.Value},
		"bad signature":     {Name: auth.SessionCookieName, Value: strings.Split(valid.Value, ".")[0] + ".AAAA"},
		"unsigned token":    {Name: auth.SessionCookieName, Value: strings.Split(valid.Value, ".")[0]},
		"unknown session":   unknown,
		"wrong cookie name": {Name: "session", Value: valid.Value},
	}
	for name, ck := range cases {
		t.Run(name, func(t *testing.T) {
			rec := app.do(http.MethodGet, "/api/me", ck)
			if rec.Code != http.StatusUnauthorized {
				t.Errorf("status %d, want 401", rec.Code)
			}
		})
	}

	t.Run("expired session", func(t *testing.T) {
		if err := app.db.Model(&models.Session{}).Where("1 = 1").
			Update("expires_at", time.Now().Add(-time.Minute)).Error; err != nil {
			t.Fatal(err)
		}
		if rec := app.do(http.MethodGet, "/api/me", valid); rec.Code != http.StatusUnauthorized {
			t.Errorf("status %d, want 401", rec.Code)
		}
	})

	t.Run("unknown api route still requires auth", func(t *testing.T) {
		if rec := app.do(http.MethodGet, "/api/does-not-exist"); rec.Code != http.StatusUnauthorized {
			t.Errorf("status %d, want 401", rec.Code)
		}
	})
}

func TestLogoutInvalidatesSession(t *testing.T) {
	app := newTestApp(t)
	app.discord.expect("code", profile("7", "bob", "", ""))
	session := app.login("code")
	app.me(session) // works before logout

	rec := app.do(http.MethodPost, "/auth/logout", session)
	if rec.Code != http.StatusNoContent {
		t.Fatalf("logout status %d, want 204", rec.Code)
	}
	cleared := findCookie(t, rec, auth.SessionCookieName)
	if cleared.Value != "" || cleared.MaxAge >= 0 {
		t.Errorf("cookie not cleared: value=%q MaxAge=%d", cleared.Value, cleared.MaxAge)
	}
	if n := app.count(&models.Session{}); n != 0 {
		t.Errorf("sessions after logout = %d, want 0", n)
	}
	// Replaying the old cookie must fail.
	if rec := app.do(http.MethodGet, "/api/me", session); rec.Code != http.StatusUnauthorized {
		t.Errorf("/api/me after logout: status %d, want 401", rec.Code)
	}
	// The user and lists are untouched.
	if app.count(&models.User{}) != 1 || app.count(&models.TVList{}) != 1 || app.count(&models.MovieList{}) != 1 {
		t.Error("logout removed user data")
	}
}

func TestLogoutOnlyEndsCurrentSession(t *testing.T) {
	app := newTestApp(t)
	app.discord.expect("phone", profile("7", "bob", "", ""))
	app.discord.expect("laptop", profile("7", "bob", "", ""))
	phone := app.login("phone")
	laptop := app.login("laptop")

	app.do(http.MethodPost, "/auth/logout", phone)

	if rec := app.do(http.MethodGet, "/api/me", phone); rec.Code != http.StatusUnauthorized {
		t.Errorf("phone session still valid: %d", rec.Code)
	}
	app.me(laptop)
}

func TestLogoutWithoutSessionIsHarmless(t *testing.T) {
	app := newTestApp(t)
	if rec := app.do(http.MethodPost, "/auth/logout"); rec.Code != http.StatusNoContent {
		t.Errorf("status %d, want 204", rec.Code)
	}
	if rec := app.do(http.MethodGet, "/auth/logout"); rec.Code != http.StatusMethodNotAllowed {
		t.Errorf("GET /auth/logout status %d, want 405", rec.Code)
	}
}

func TestMeReturnsTheRightUser(t *testing.T) {
	app := newTestApp(t)
	app.discord.expect("alice", profile("111", "alice", "Alice A", ""))
	app.discord.expect("bob", profile("222", "bob", "Bob B", ""))
	aliceSession := app.login("alice")
	bobSession := app.login("bob")

	alice := app.me(aliceSession)
	bob := app.me(bobSession)

	if alice["discord_id"] != "111" || alice["username"] != "alice" || alice["global_name"] != "Alice A" {
		t.Errorf("alice got %v", alice)
	}
	if bob["discord_id"] != "222" || bob["username"] != "bob" || bob["global_name"] != "Bob B" {
		t.Errorf("bob got %v", bob)
	}
	if alice["id"] == bob["id"] || alice["tv_list_id"] == bob["tv_list_id"] || alice["movie_list_id"] == bob["movie_list_id"] {
		t.Error("users share ids")
	}
	for _, key := range []string{"tv_list_id", "movie_list_id"} {
		if v, _ := alice[key].(float64); v == 0 {
			t.Errorf("alice %s missing: %v", key, alice[key])
		}
	}

	// Each user's list ids match the database.
	var tv models.TVList
	app.db.Joins("JOIN users ON users.id = tv_lists.user_id").Where("users.discord_id = ?", "111").Take(&tv)
	if alice["tv_list_id"] != float64(tv.ID) {
		t.Errorf("alice tv_list_id %v, db has %d", alice["tv_list_id"], tv.ID)
	}
	// Tokens never leak into the response.
	for _, key := range []string{"discord_access_token", "access_token", "token_hash"} {
		if _, ok := alice[key]; ok {
			t.Errorf("/api/me exposes %s", key)
		}
	}
}

func TestCallbackRejectsBadState(t *testing.T) {
	app := newTestApp(t)
	app.discord.expect("code", profile("1", "alice", "", ""))
	state, stateCookie := app.startLogin()
	_, otherCookie := app.startLogin()

	cases := []struct {
		name   string
		query  string
		cookie *http.Cookie
	}{
		{"no state cookie", "?code=code&state=" + state, nil},
		{"no state param", "?code=code", stateCookie},
		{"mismatched state", "?code=code&state=wrong", stateCookie},
		{"cookie from another login", "?code=code&state=" + state, otherCookie},
		{"forged cookie", "?code=code&state=abc", &http.Cookie{Name: auth.StateCookieName, Value: "abc.def"}},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			rec := app.do(http.MethodGet, "/auth/discord/callback"+tc.query, tc.cookie)
			if rec.Code != http.StatusBadRequest {
				t.Errorf("status %d, want 400", rec.Code)
			}
		})
	}

	if tokenCalls, _ := app.discord.calls(); tokenCalls != 0 {
		t.Errorf("Discord was called %d times despite bad state", tokenCalls)
	}
	if n := app.count(&models.User{}); n != 0 {
		t.Errorf("users = %d, want 0", n)
	}
}

func TestCallbackHandlesDiscordFailures(t *testing.T) {
	app := newTestApp(t)

	t.Run("user denied consent", func(t *testing.T) {
		state, ck := app.startLogin()
		rec := app.do(http.MethodGet, "/auth/discord/callback?error=access_denied&state="+state, ck)
		if rec.Code != http.StatusUnauthorized {
			t.Errorf("status %d, want 401", rec.Code)
		}
	})
	t.Run("missing code", func(t *testing.T) {
		state, ck := app.startLogin()
		rec := app.do(http.MethodGet, "/auth/discord/callback?state="+state, ck)
		if rec.Code != http.StatusBadRequest {
			t.Errorf("status %d, want 400", rec.Code)
		}
	})
	t.Run("code rejected by Discord", func(t *testing.T) {
		state, ck := app.startLogin()
		rec := app.do(http.MethodGet, "/auth/discord/callback?code=unknown&state="+state, ck)
		if rec.Code != http.StatusBadGateway {
			t.Errorf("status %d, want 502", rec.Code)
		}
		if _, ok := cookieIn(rec.Result().Cookies(), auth.SessionCookieName); ok {
			t.Error("session cookie set after failed exchange")
		}
	})

	if n := app.count(&models.User{}); n != 0 {
		t.Errorf("users = %d, want 0", n)
	}
}

func TestSessionTokensAreNotStoredInPlaintext(t *testing.T) {
	app := newTestApp(t)
	app.discord.expect("code", profile("1", "alice", "", ""))
	session := app.login("code")
	rawToken := strings.Split(session.Value, ".")[0]

	var sess models.Session
	if err := app.db.Take(&sess).Error; err != nil {
		t.Fatal(err)
	}
	if sess.TokenHash != auth.HashToken(rawToken) {
		t.Error("token_hash is not the SHA-256 of the cookie token")
	}
	if strings.Contains(sess.TokenHash, rawToken) {
		t.Error("raw session token stored")
	}
	if strings.Contains(sess.DiscordAccessToken, "access-code") || strings.Contains(sess.DiscordRefreshToken, "refresh-code") {
		t.Error("Discord tokens stored in plaintext")
	}
	if sess.TokenExpiry.Before(time.Now().Add(6 * 24 * time.Hour)) {
		t.Errorf("token_expiry %v does not reflect expires_in", sess.TokenExpiry)
	}
}

func TestHealthz(t *testing.T) {
	app := newTestApp(t)
	rec := app.do(http.MethodGet, "/healthz")
	if rec.Code != http.StatusOK || !strings.Contains(rec.Body.String(), `"ok"`) {
		t.Errorf("status %d body %s", rec.Code, rec.Body.String())
	}
}

// forgeSignedCookie produces a correctly signed session cookie for an arbitrary
// token by running a real login and swapping the database row's hash. It
// proves the middleware checks the database, not just the signature.
func forgeSignedCookie(t *testing.T, app *testApp, label string) *http.Cookie {
	t.Helper()
	app.discord.expect("forge-"+label, profile("999", "forger", "", ""))
	ck := app.login("forge-" + label)
	if err := app.db.Where("token_hash = ?", auth.HashToken(strings.Split(ck.Value, ".")[0])).
		Delete(&models.Session{}).Error; err != nil {
		t.Fatal(err)
	}
	return ck
}

func cookieIn(cookies []*http.Cookie, name string) (*http.Cookie, bool) {
	for _, c := range cookies {
		if c.Name == name && c.Value != "" {
			return c, true
		}
	}
	return nil, false
}
