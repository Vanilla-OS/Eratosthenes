package db

import (
	"encoding/json"
	"log"

	"github.com/mirkobrombin/go-slipstream/pkg/engine"
	"github.com/mirkobrombin/go-slipstream/pkg/wal"
	"github.com/vanilla-os/eratosthenes/internal/config"
	"github.com/vanilla-os/eratosthenes/internal/models"
)

var DB *engine.Bitcask[models.Package]

func InitDB() {
	w, err := wal.NewManager(config.Instance.DbPath)
	if err != nil {
		log.Fatal(err)
	}

	codec := func(p models.Package) ([]byte, error) {
		return json.Marshal(p)
	}
	decoder := func(b []byte) (models.Package, error) {
		var p models.Package
		err := json.Unmarshal(b, &p)
		return p, err
	}

	DB = engine.NewBitcask[models.Package](w, codec, decoder)

	if err := DB.Engine().Recover(); err != nil {
		log.Println("Warning: failed to recover DB:", err)
	}

	DB.AddIndex("name", func(p models.Package) string {
		return p.Name
	})
}

func Close() {
	if DB != nil {
		DB.Close()
	}
}
