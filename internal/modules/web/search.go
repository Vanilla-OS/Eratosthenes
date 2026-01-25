package web

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/mirkobrombin/go-module-router/v2/pkg/core"
	"github.com/mirkobrombin/go-module-router/v2/pkg/router"
	"github.com/vanilla-os/eratosthenes/internal/config"
	"github.com/vanilla-os/eratosthenes/internal/db"
	"github.com/vanilla-os/eratosthenes/internal/models"
)

type SearchEndpoint struct {
	Meta core.Pattern `method:"GET" path:"/search"`
}

func (e *SearchEndpoint) Handle(ctx context.Context) (any, error) {
	w, ok := ctx.Value(router.CtxKeyResponseWriter).(http.ResponseWriter)
	if !ok {
		return nil, nil
	}
	r, ok := ctx.Value(router.CtxKeyRequest).(*http.Request)
	if !ok {
		return nil, nil
	}

	query := r.URL.Query().Get("q")
	branch := r.URL.Query().Get("branch")
	if branch == "" {
		branch = ReadCookie(r, "branch", "main")
	}
	arch := r.URL.Query().Get("arch")
	if arch == "" {
		arch = ReadCookie(r, "arch", "amd64")
	}

	if query == "" {
		Render(w, "templates/404.html", nil)
		return nil, nil
	}

	var packages []models.Package
	prefix := fmt.Sprintf("%s|%s|", branch, arch)

	keys, err := db.DB.Engine().Keys()
	if err != nil {
		log.Println("Error fetching keys:", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return nil, nil
	}

	queryLower := strings.ToLower(query)

	for _, key := range keys {
		if !strings.HasPrefix(key, prefix) {
			continue
		}

		name := strings.TrimPrefix(key, prefix)
		if strings.Contains(strings.ToLower(name), queryLower) {
			p, err := db.DB.Get(r.Context(), key)
			if err == nil {
				packages = append(packages, p)
			}
		}
	}

	if r.Header.Get("Accept") == "application/json" {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(packages)
		return nil, nil
	}

	data := map[string]any{
		"Query":         query,
		"Packages":      packages,
		"Branch":        branch,
		"CurrentArch":   arch,
		"Archs":         config.Instance.Archs,
		"ShowSearchBar": true,
	}

	Render(w, "templates/search.html", data)
	return nil, nil
}
