package models

type Package struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	Version     string `json:"version"`
	Description string `json:"description"`
	Section     string `json:"section"`
	Homepage    string `json:"homepage"`
	Maintainer  string `json:"maintainer"`
	Depends     string `json:"depends"`
	Recommends  string `json:"recommends"`
	Suggests    string `json:"suggests"`
	Conflicts   string `json:"conflicts"`
	Replaces    string `json:"replaces"`
	Provides    string `json:"provides"`
	Filename    string `json:"filename"`
	Branch      string `json:"branch"`
	Arch        string `json:"arch"`
}
