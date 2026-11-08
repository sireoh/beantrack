package auth

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

// OAuthScopes are the Discord scopes BeanTrack requests.
const OAuthScopes = "identify email"

const discordCDN = "https://cdn.discordapp.com"

// DiscordClient talks to the Discord OAuth2 and user APIs.
type DiscordClient struct {
	APIBaseURL   string
	ClientID     string
	ClientSecret string
	RedirectURI  string
	HTTP         *http.Client
}

// TokenResponse is Discord's reply to a token exchange.
type TokenResponse struct {
	AccessToken  string `json:"access_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int64  `json:"expires_in"`
	RefreshToken string `json:"refresh_token"`
	Scope        string `json:"scope"`
}

// DiscordUser is the subset of GET /users/@me that BeanTrack uses.
type DiscordUser struct {
	ID            string  `json:"id"`
	Username      string  `json:"username"`
	GlobalName    *string `json:"global_name"`
	Discriminator string  `json:"discriminator"`
	Avatar        *string `json:"avatar"`
	Email         *string `json:"email"`
}

// AvatarURL returns the user's avatar on Discord's CDN, or Discord's default
// avatar if they have not set one.
func (u *DiscordUser) AvatarURL() string {
	if u.Avatar != nil && *u.Avatar != "" {
		ext := "png"
		if strings.HasPrefix(*u.Avatar, "a_") {
			ext = "gif"
		}
		return fmt.Sprintf("%s/avatars/%s/%s.%s", discordCDN, u.ID, *u.Avatar, ext)
	}
	// Default avatar index: (id >> 22) % 6 for the new username system,
	// discriminator % 5 for legacy accounts.
	index := 0
	if u.Discriminator == "" || u.Discriminator == "0" {
		if id, err := strconv.ParseUint(u.ID, 10, 64); err == nil {
			index = int((id >> 22) % 6)
		}
	} else if d, err := strconv.Atoi(u.Discriminator); err == nil {
		index = d % 5
	}
	return fmt.Sprintf("%s/embed/avatars/%d.png", discordCDN, index)
}

// ExchangeCode swaps an authorization code for tokens.
func (d *DiscordClient) ExchangeCode(ctx context.Context, code string) (*TokenResponse, error) {
	form := url.Values{
		"grant_type":   {"authorization_code"},
		"code":         {code},
		"redirect_uri": {d.RedirectURI},
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, d.APIBaseURL+"/oauth2/token", strings.NewReader(form.Encode()))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "application/json")
	req.SetBasicAuth(url.QueryEscape(d.ClientID), url.QueryEscape(d.ClientSecret))

	var tok TokenResponse
	if err := d.do(req, &tok); err != nil {
		return nil, fmt.Errorf("discord token exchange: %w", err)
	}
	if tok.AccessToken == "" {
		return nil, fmt.Errorf("discord token exchange: response had no access_token")
	}
	return &tok, nil
}

// FetchCurrentUser returns the profile of the user the access token belongs to.
func (d *DiscordClient) FetchCurrentUser(ctx context.Context, accessToken string) (*DiscordUser, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, d.APIBaseURL+"/users/@me", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+accessToken)
	req.Header.Set("Accept", "application/json")

	var u DiscordUser
	if err := d.do(req, &u); err != nil {
		return nil, fmt.Errorf("discord fetch user: %w", err)
	}
	if u.ID == "" || u.Username == "" {
		return nil, fmt.Errorf("discord fetch user: response missing id or username")
	}
	return &u, nil
}

func (d *DiscordClient) do(req *http.Request, out any) error {
	client := d.HTTP
	if client == nil {
		client = &http.Client{Timeout: 10 * time.Second}
	}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(io.LimitReader(resp.Body, 1<<20))
	if err != nil {
		return err
	}
	if resp.StatusCode != http.StatusOK {
		// Discord error bodies are short JSON and contain no secrets.
		return fmt.Errorf("unexpected status %d: %s", resp.StatusCode, truncate(string(body), 200))
	}
	return json.Unmarshal(body, out)
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "..."
}
