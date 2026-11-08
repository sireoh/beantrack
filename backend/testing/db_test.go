package apitest

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/beantrack/backend/internal/config"
	"github.com/beantrack/backend/internal/models"
)

func TestDatabaseFileLivesInDataDir(t *testing.T) {
	app := newTestApp(t)
	path := filepath.Join(app.cfg.DataDir, config.DBFileName)
	if _, err := os.Stat(path); err != nil {
		t.Fatalf("database file not at %s: %v", path, err)
	}
}

// Pragmas are per-connection, so check several pooled connections at once.
func TestPragmasApplyToEveryConnection(t *testing.T) {
	app := newTestApp(t)
	sqlDB, err := app.db.DB()
	if err != nil {
		t.Fatal(err)
	}
	ctx := context.Background()

	const n = 4
	for i := 0; i < n; i++ {
		conn, err := sqlDB.Conn(ctx)
		if err != nil {
			t.Fatal(err)
		}
		defer conn.Close()

		var journal string
		var fk, busy int
		if err := conn.QueryRowContext(ctx, "PRAGMA journal_mode").Scan(&journal); err != nil {
			t.Fatal(err)
		}
		if err := conn.QueryRowContext(ctx, "PRAGMA foreign_keys").Scan(&fk); err != nil {
			t.Fatal(err)
		}
		if err := conn.QueryRowContext(ctx, "PRAGMA busy_timeout").Scan(&busy); err != nil {
			t.Fatal(err)
		}
		if !strings.EqualFold(journal, "wal") || fk != 1 || busy != 5000 {
			t.Errorf("conn %d: journal_mode=%s foreign_keys=%d busy_timeout=%d", i, journal, fk, busy)
		}
	}
}

func TestForeignKeysAreEnforced(t *testing.T) {
	app := newTestApp(t)
	err := app.db.Create(&models.TVList{UserID: 424242}).Error
	if err == nil {
		t.Fatal("inserted a tv list for a user that does not exist")
	}
}

func TestOneListOfEachKindPerUser(t *testing.T) {
	app := newTestApp(t)
	app.discord.expect("code", profile("5", "carol", "", ""))
	app.login("code")

	var user models.User
	app.db.Take(&user)
	if err := app.db.Create(&models.TVList{UserID: user.ID}).Error; err == nil {
		t.Error("second tv list allowed")
	}
	if err := app.db.Create(&models.MovieList{UserID: user.ID}).Error; err == nil {
		t.Error("second movie list allowed")
	}
}

func TestDeletingUserCascades(t *testing.T) {
	app := newTestApp(t)
	app.discord.expect("code", profile("6", "dave", "", ""))
	app.login("code")

	if err := app.db.Where("1 = 1").Delete(&models.User{}).Error; err != nil {
		t.Fatal(err)
	}
	for name, model := range map[string]any{
		"sessions": &models.Session{}, "tv_lists": &models.TVList{}, "movie_lists": &models.MovieList{},
	} {
		if n := app.count(model); n != 0 {
			t.Errorf("%s left behind: %d", name, n)
		}
	}
}
