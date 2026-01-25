package config

import (
	"log"

	"github.com/vanilla-os/sdk/pkg/v1/conf"
)

type Config struct {
	Port           int               `json:"port"`
	Debug          bool              `json:"debug"`
	DbPath         string            `json:"db_path"`
	Branches       map[string]string `json:"branches"`
	Archs          []string          `json:"archs"`
	RepoComponents []string          `json:"repo_components"`
}

var Instance *Config

func Default() *Config {
	return &Config{
		Port:   6001,
		Debug:  true,
		DbPath: "eratosthenes_data",
		Branches: map[string]string{
			"main":    "https://repo3.vanillaos.org/20251129T023004Z/dists/sid/@/@/Packages",
			"testing": "https://repo3.vanillaos.org/20260116T142445Z/dists/sid/@/@/Packages",
		},
		Archs:          []string{"amd64", "arm64", "i386"},
		RepoComponents: []string{"main", "contrib", "non-free-firmware", "non-free"},
	}
}

func Load() {
	Instance = Default()

	loaded, err := conf.NewBuilder[Config]("eratosthenes").
		WithOptional(true).
		Build()

	if err != nil {
		log.Printf("Error loading config: %v. Using defaults.", err)
		return
	}

	if loaded.Port != 0 {
		Instance.Port = loaded.Port
	}
	if loaded.DbPath != "" {
		Instance.DbPath = loaded.DbPath
	}
	if len(loaded.Branches) > 0 {
		Instance.Branches = loaded.Branches
	}
	if len(loaded.Archs) > 0 {
		Instance.Archs = loaded.Archs
	}
	if len(loaded.RepoComponents) > 0 {
		Instance.RepoComponents = loaded.RepoComponents
	}
}
