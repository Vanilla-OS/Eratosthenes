package web

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/mirkobrombin/go-module-router/v2/pkg/core"
	"github.com/mirkobrombin/go-module-router/v2/pkg/router"
	"github.com/mirkobrombin/go-warp/v1/cache"
	"github.com/vanilla-os/eratosthenes/internal/config"
	"github.com/vanilla-os/eratosthenes/internal/db"
	"github.com/vanilla-os/eratosthenes/internal/models"
)

type PackageEndpoint struct {
	Meta  core.Pattern `method:"GET" path:"/package/{name}"`
	Cache cache.Cache[models.Package]
}

type TabItem struct {
	Name  string
	ID    string
	Items []models.Package
}

func (e *PackageEndpoint) Handle(ctx context.Context) (any, error) {
	w, ok := ctx.Value(router.CtxKeyResponseWriter).(http.ResponseWriter)
	if !ok {
		return nil, nil
	}
	r, ok := ctx.Value(router.CtxKeyRequest).(*http.Request)
	if !ok {
		return nil, nil
	}

	name := r.PathValue("name")
	if name == "" {
		Render(w, "templates/404.html", nil)
		return nil, nil
	}

	branch := ReadCookie(r, "branch", "main")
	arch := r.URL.Query().Get("arch")
	if arch == "" {
		arch = ReadCookie(r, "arch", "amd64")
	}

	key := fmt.Sprintf("%s|%s|%s", branch, arch, name)

	if cached, found, _ := e.Cache.Get(ctx, key); found {
		renderPackage(w, cached, branch, arch)
		return nil, nil
	}

	p, err := db.DB.Get(ctx, key)
	if err != nil {
		log.Println("Error fetching package:", err)
		Render(w, "templates/404.html", nil)
		return nil, nil
	}

	_ = e.Cache.Set(ctx, key, p, 5*time.Minute)

	renderPackage(w, p, branch, arch)
	return nil, nil
}

func renderPackage(w http.ResponseWriter, p models.Package, branch, arch string) {
	tabs := []TabItem{
		{Name: "Depends", ID: "depends", Items: fetchResolvable(p.Depends, branch, arch)},
		{Name: "Recommends", ID: "recommends", Items: fetchResolvable(p.Recommends, branch, arch)},
		{Name: "Suggests", ID: "suggests", Items: fetchResolvable(p.Suggests, branch, arch)},
		{Name: "Conflicts", ID: "conflicts", Items: fetchResolvable(p.Conflicts, branch, arch)},
		{Name: "Replaces", ID: "replaces", Items: fetchResolvable(p.Replaces, branch, arch)},
		{Name: "Provides", ID: "provides", Items: fetchResolvable(p.Provides, branch, arch)},
	}

	data := map[string]any{
		"Package":       p,
		"Tabs":          tabs,
		"Branch":        branch,
		"CurrentArch":   arch,
		"Archs":         config.Instance.Archs,
		"ShowSearchBar": true,
	}

	Render(w, "templates/package.html", data)
}

func fetchResolvable(listStr, branch, arch string) []models.Package {
	if listStr == "" {
		return nil
	}

	var pkgs []models.Package
	parts := strings.SplitSeq(listStr, ", ")

	for part := range parts {
		name := strings.Split(part, " ")[0]
		key := fmt.Sprintf("%s|%s|%s", branch, arch, name)

		p, err := db.DB.Get(context.Background(), key)
		if err == nil {
			pkgs = append(pkgs, p)
		}
	}
	return pkgs
}
