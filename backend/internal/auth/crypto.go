package auth

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"errors"
	"strings"
)

// Purposes bind a signature to one cookie so a value signed for one use
// cannot be replayed as another.
const (
	purposeSession = "session"
	purposeState   = "oauth-state"
)

const sealedPrefix = "v1:"

// deriveKey derives an independent 32-byte key from SESSION_SECRET for one use.
func deriveKey(secret, label string) []byte {
	m := hmac.New(sha256.New, []byte(secret))
	m.Write([]byte("beantrack/" + label))
	return m.Sum(nil)
}

// randomToken returns n random bytes, base64url-encoded without padding.
func randomToken(n int) (string, error) {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	return base64.RawURLEncoding.EncodeToString(b), nil
}

// HashToken returns the hex SHA-256 of a session token. This is what the
// sessions table stores.
func HashToken(token string) string {
	sum := sha256.Sum256([]byte(token))
	return hex.EncodeToString(sum[:])
}

type signer struct{ key []byte }

func (s signer) mac(purpose, value string) []byte {
	m := hmac.New(sha256.New, s.key)
	m.Write([]byte(purpose))
	m.Write([]byte{0})
	m.Write([]byte(value))
	return m.Sum(nil)
}

// sign returns "value.signature".
func (s signer) sign(purpose, value string) string {
	return value + "." + base64.RawURLEncoding.EncodeToString(s.mac(purpose, value))
}

// verify checks a value produced by sign and returns the original value.
func (s signer) verify(purpose, signed string) (string, bool) {
	i := strings.LastIndexByte(signed, '.')
	if i <= 0 || i == len(signed)-1 {
		return "", false
	}
	value, sig := signed[:i], signed[i+1:]
	got, err := base64.RawURLEncoding.DecodeString(sig)
	if err != nil {
		return "", false
	}
	if !hmac.Equal(got, s.mac(purpose, value)) {
		return "", false
	}
	return value, true
}

// tokenBox encrypts Discord tokens before they are written to the database
// (and therefore to the Litestream replica).
type tokenBox struct{ aead cipher.AEAD }

func newTokenBox(key []byte) (*tokenBox, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	aead, err := cipher.NewGCM(block)
	if err != nil {
		return nil, err
	}
	return &tokenBox{aead: aead}, nil
}

func (b *tokenBox) seal(plaintext string) (string, error) {
	if plaintext == "" {
		return "", nil
	}
	nonce := make([]byte, b.aead.NonceSize())
	if _, err := rand.Read(nonce); err != nil {
		return "", err
	}
	out := b.aead.Seal(nonce, nonce, []byte(plaintext), nil)
	return sealedPrefix + base64.RawStdEncoding.EncodeToString(out), nil
}

func (b *tokenBox) open(sealed string) (string, error) {
	if sealed == "" {
		return "", nil
	}
	if !strings.HasPrefix(sealed, sealedPrefix) {
		return "", errors.New("unknown token encoding")
	}
	raw, err := base64.RawStdEncoding.DecodeString(sealed[len(sealedPrefix):])
	if err != nil {
		return "", err
	}
	ns := b.aead.NonceSize()
	if len(raw) < ns {
		return "", errors.New("sealed token too short")
	}
	plain, err := b.aead.Open(nil, raw[:ns], raw[ns:], nil)
	if err != nil {
		return "", err
	}
	return string(plain), nil
}
