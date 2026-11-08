// Package db opens the SQLite database and runs migrations.
package db

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/glebarez/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"github.com/beantrack/backend/internal/config"
	"github.com/beantrack/backend/internal/models"
)

// Connection settings are passed in the DSN so the driver applies them to
// every pooled connection; busy_timeout and foreign_keys are per-connection
// settings, so a one-off PRAGMA would only reach one of them.
//
// The app never runs wal_checkpoint itself: Litestream owns checkpointing.
// SQLite's default auto-checkpoint is left on, which Litestream supports.
//
// _txlock=immediate makes every transaction take the write lock up front,
// which avoids SQLITE_BUSY on read-to-write lock upgrades.
var dsnParams = []string{
	"_pragma=busy_timeout(5000)",
	"_pragma=journal_mode(WAL)",
	"_pragma=foreign_keys(1)",
	"_pragma=synchronous(NORMAL)",
	"_txlock=immediate",
}

// Open creates dataDir if needed, opens $dataDir/beantrack.db, checks the
// connection settings and runs auto-migrations.
func Open(dataDir string) (*gorm.DB, error) {
	if err := os.MkdirAll(dataDir, 0o750); err != nil {
		return nil, fmt.Errorf("creating data dir %q: %w", dataDir, err)
	}
	path := filepath.Join(dataDir, config.DBFileName)
	dsn := path + "?" + strings.Join(dsnParams, "&")

	gdb, err := gorm.Open(sqlite.Open(dsn), &gorm.Config{
		TranslateError: true,
		NowFunc:        func() time.Time { return time.Now().UTC() },
		Logger: logger.New(log.New(os.Stdout, "", log.LstdFlags), logger.Config{
			SlowThreshold:             500 * time.Millisecond,
			LogLevel:                  logger.Warn,
			IgnoreRecordNotFoundError: true,
		}),
	})
	if err != nil {
		return nil, fmt.Errorf("opening database %q: %w", path, err)
	}

	if err := verifyPragmas(gdb); err != nil {
		Close(gdb)
		return nil, err
	}
	if err := gdb.AutoMigrate(models.All()...); err != nil {
		Close(gdb)
		return nil, fmt.Errorf("running migrations: %w", err)
	}
	return gdb, nil
}

// Close closes the underlying connection pool.
func Close(gdb *gorm.DB) error {
	sqlDB, err := gdb.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}

func verifyPragmas(gdb *gorm.DB) error {
	var journalMode string
	var foreignKeys, busyTimeout int
	if err := gdb.Raw("PRAGMA journal_mode").Scan(&journalMode).Error; err != nil {
		return fmt.Errorf("reading journal_mode: %w", err)
	}
	if err := gdb.Raw("PRAGMA foreign_keys").Scan(&foreignKeys).Error; err != nil {
		return fmt.Errorf("reading foreign_keys: %w", err)
	}
	if err := gdb.Raw("PRAGMA busy_timeout").Scan(&busyTimeout).Error; err != nil {
		return fmt.Errorf("reading busy_timeout: %w", err)
	}
	if !strings.EqualFold(journalMode, "wal") || foreignKeys != 1 || busyTimeout != 5000 {
		return fmt.Errorf("unexpected SQLite settings: journal_mode=%s foreign_keys=%d busy_timeout=%d", journalMode, foreignKeys, busyTimeout)
	}
	return nil
}
