// Package auth implements Discord OAuth2 sign-in, sessions and the auth
// middleware.
package auth

import (
	"context"
	"crypto/subtle"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"net/url"
	"time"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"

	"github.com/beantrack/backend/internal/config"
	"github.com/beantrack/backend/internal/models"
)

const (
	SessionCookieName = "bt_session"
	StateCookieName   = "bt_oauth_state"

	stateCookiePath = "/auth/discord"
	stateTTL        = 10 * time.Minute

	ctxUserKey    = "auth.user"
	ctxSessionKey = "auth.session"
)

// Service holds everything the auth handlers need.
type Service struct {
	cfg     *config.Config
	db      *gorm.DB
	discord *DiscordClient
	signer  signer
	box     *tokenBox
	log     *slog.Logger
	now     func() time.Time
}

// NewService builds the auth service. httpClient is used for calls to Discord.
func NewService(cfg *config.Config, db *gorm.DB, httpClient *http.Client, log *slog.Logger) (*Service, error) {
	box, err := newTokenBox(deriveKey(cfg.SessionSecret, "discord-token-encryption"))
	if err != nil {
		return nil, err
	}
	if log == nil {
		log = slog.Default()
	}
	return &Service{
		cfg: cfg,
		db:  db,
		discord: &DiscordClient{
			APIBaseURL:   cfg.DiscordAPIBaseURL,
			ClientID:     cfg.DiscordClientID,
			ClientSecret: cfg.DiscordClientSecret,
			RedirectURI:  cfg.DiscordRedirectURI,
			HTTP:         httpClient,
		},
		signer: signer{key: deriveKey(cfg.SessionSecret, "cookie-signing")},
		box:    box,
		log:    log,
		now:    func() time.Time { return time.Now().UTC() },
	}, nil
}

// Login redirects the browser to Discord's consent screen. A random state value
// goes both in the URL and in a signed, short-lived cookie; Callback requires
// them to match, which blocks login CSRF.
func (s *Service) Login(c echo.Context) error {
	state, err := randomToken(32)
	if err != nil {
		return fmt.Errorf("generating oauth state: %w", err)
	}
	c.SetCookie(&http.Cookie{
		Name:     StateCookieName,
		Value:    s.signer.sign(purposeState, state),
		Path:     stateCookiePath,
		MaxAge:   int(stateTTL.Seconds()),
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteLaxMode,
	})

	q := url.Values{
		"response_type": {"code"},
		"client_id":     {s.cfg.DiscordClientID},
		"scope":         {OAuthScopes},
		"redirect_uri":  {s.cfg.DiscordRedirectURI},
		"state":         {state},
		"prompt":        {"none"}, // skip the consent screen if already authorized
	}
	return c.Redirect(http.StatusFound, s.cfg.DiscordAuthorizeURL+"?"+q.Encode())
}

// Callback finishes the OAuth flow: it checks state, exchanges the code,
// fetches the Discord profile, creates or updates the user and starts a session.
func (s *Service) Callback(c echo.Context) error {
	// The state cookie is single-use whatever happens next.
	clearCookie(c, StateCookieName, stateCookiePath)

	ck, err := c.Cookie(StateCookieName)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "missing oauth state; start again at /auth/discord/login")
	}
	expected, ok := s.signer.verify(purposeState, ck.Value)
	got := c.QueryParam("state")
	if !ok || got == "" || subtle.ConstantTimeCompare([]byte(expected), []byte(got)) != 1 {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid oauth state")
	}

	if c.QueryParam("error") != "" {
		return echo.NewHTTPError(http.StatusUnauthorized, "discord authorization was not granted")
	}
	code := c.QueryParam("code")
	if code == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "missing authorization code")
	}

	ctx := c.Request().Context()
	tok, err := s.discord.ExchangeCode(ctx, code)
	if err != nil {
		s.log.WarnContext(ctx, "discord code exchange failed", "err", err)
		return echo.NewHTTPError(http.StatusBadGateway, "could not complete sign-in with Discord")
	}
	profile, err := s.discord.FetchCurrentUser(ctx, tok.AccessToken)
	if err != nil {
		s.log.WarnContext(ctx, "discord profile fetch failed", "err", err)
		return echo.NewHTTPError(http.StatusBadGateway, "could not complete sign-in with Discord")
	}

	rawToken, sess, err := s.completeLogin(ctx, profile, tok)
	if err != nil {
		return fmt.Errorf("completing login: %w", err)
	}
	s.setSessionCookie(c, rawToken, sess.ExpiresAt)
	s.log.InfoContext(ctx, "user signed in", "user_id", sess.UserID)
	return c.Redirect(http.StatusSeeOther, s.cfg.LoginRedirectURL)
}

// completeLogin upserts the user, makes sure both lists exist and creates a
// session, all in one transaction. A first sign-in therefore creates the user
// row, TV list and movie list together or not at all.
func (s *Service) completeLogin(ctx context.Context, p *DiscordUser, tok *TokenResponse) (string, *models.Session, error) {
	rawToken, err := randomToken(32)
	if err != nil {
		return "", nil, err
	}
	access, err := s.box.seal(tok.AccessToken)
	if err != nil {
		return "", nil, err
	}
	refresh, err := s.box.seal(tok.RefreshToken)
	if err != nil {
		return "", nil, err
	}

	now := s.now()
	sess := &models.Session{
		TokenHash:           HashToken(rawToken),
		DiscordAccessToken:  access,
		DiscordRefreshToken: refresh,
		TokenExpiry:         now.Add(time.Duration(tok.ExpiresIn) * time.Second),
		ExpiresAt:           now.Add(s.cfg.SessionTTL),
	}

	err = s.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		// Insert, or refresh the Discord-owned fields on repeat logins. Email
		// is only overwritten when Discord sent one.
		updates := []string{"username", "global_name", "avatar_url", "updated_at"}
		if p.Email != nil {
			updates = append(updates, "email")
		}
		incoming := models.User{
			DiscordID:  p.ID,
			Username:   p.Username,
			GlobalName: p.GlobalName,
			AvatarURL:  p.AvatarURL(),
			Email:      p.Email,
		}
		if err := tx.Omit(clause.Associations).Clauses(clause.OnConflict{
			Columns:   []clause.Column{{Name: "discord_id"}},
			DoUpdates: clause.AssignmentColumns(updates),
		}).Create(&incoming).Error; err != nil {
			return fmt.Errorf("upserting user: %w", err)
		}

		var user models.User
		if err := tx.Where("discord_id = ?", p.ID).Take(&user).Error; err != nil {
			return fmt.Errorf("loading user: %w", err)
		}

		noop := clause.OnConflict{Columns: []clause.Column{{Name: "user_id"}}, DoNothing: true}
		if err := tx.Clauses(noop).Create(&models.TVList{UserID: user.ID}).Error; err != nil {
			return fmt.Errorf("creating tv list: %w", err)
		}
		if err := tx.Clauses(noop).Create(&models.MovieList{UserID: user.ID}).Error; err != nil {
			return fmt.Errorf("creating movie list: %w", err)
		}

		// Housekeeping: drop expired sessions while we hold the write lock.
		if err := tx.Where("expires_at <= ?", now).Delete(&models.Session{}).Error; err != nil {
			return fmt.Errorf("pruning sessions: %w", err)
		}

		sess.UserID = user.ID
		if err := tx.Omit(clause.Associations).Create(sess).Error; err != nil {
			return fmt.Errorf("creating session: %w", err)
		}
		return nil
	})
	if err != nil {
		return "", nil, err
	}
	return rawToken, sess, nil
}

// Logout deletes the current session (if any) and clears the cookie. It is
// safe to call without a session.
func (s *Service) Logout(c echo.Context) error {
	if ck, err := c.Cookie(SessionCookieName); err == nil {
		if token, ok := s.signer.verify(purposeSession, ck.Value); ok {
			if err := s.db.WithContext(c.Request().Context()).
				Where("token_hash = ?", HashToken(token)).
				Delete(&models.Session{}).Error; err != nil {
				return fmt.Errorf("deleting session: %w", err)
			}
		}
	}
	clearCookie(c, SessionCookieName, "/")
	return c.NoContent(http.StatusNoContent)
}

// RequireSession is middleware that rejects requests without a valid session
// with 401 and otherwise stores the user and session on the context.
func (s *Service) RequireSession(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		sess, err := s.lookupSession(c)
		if err != nil {
			if !errors.Is(err, errNoSession) {
				return err
			}
			return echo.NewHTTPError(http.StatusUnauthorized, "authentication required")
		}
		c.Set(ctxSessionKey, sess)
		c.Set(ctxUserKey, &sess.User)
		return next(c)
	}
}

var errNoSession = errors.New("no valid session")

func (s *Service) lookupSession(c echo.Context) (*models.Session, error) {
	ck, err := c.Cookie(SessionCookieName)
	if err != nil {
		return nil, errNoSession
	}
	token, ok := s.signer.verify(purposeSession, ck.Value)
	if !ok {
		return nil, errNoSession
	}
	var sess models.Session
	err = s.db.WithContext(c.Request().Context()).
		Preload("User").
		Where("token_hash = ? AND expires_at > ?", HashToken(token), s.now()).
		Take(&sess).Error
	if errors.Is(err, gorm.ErrRecordNotFound) {
		return nil, errNoSession
	}
	if err != nil {
		return nil, fmt.Errorf("looking up session: %w", err)
	}
	return &sess, nil
}

// DiscordAccessToken decrypts the Discord access token stored on a session.
func (s *Service) DiscordAccessToken(sess *models.Session) (string, error) {
	return s.box.open(sess.DiscordAccessToken)
}

// CurrentUser returns the user set by RequireSession.
func CurrentUser(c echo.Context) *models.User {
	u, _ := c.Get(ctxUserKey).(*models.User)
	return u
}

// CurrentSession returns the session set by RequireSession.
func CurrentSession(c echo.Context) *models.Session {
	sess, _ := c.Get(ctxSessionKey).(*models.Session)
	return sess
}

func (s *Service) setSessionCookie(c echo.Context, rawToken string, expires time.Time) {
	c.SetCookie(&http.Cookie{
		Name:     SessionCookieName,
		Value:    s.signer.sign(purposeSession, rawToken),
		Path:     "/",
		Expires:  expires,
		MaxAge:   int(time.Until(expires).Seconds()),
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteLaxMode,
	})
}

func clearCookie(c echo.Context, name, path string) {
	c.SetCookie(&http.Cookie{
		Name:     name,
		Value:    "",
		Path:     path,
		MaxAge:   -1,
		Expires:  time.Unix(0, 0),
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteLaxMode,
	})
}
