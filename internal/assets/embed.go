package assets

import "embed"

//go:embed templates/* static/*
var Content embed.FS
