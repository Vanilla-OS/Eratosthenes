package cli

import (
	"context"
	"fmt"
	"io/fs"
	"net/http"

	"github.com/mirkobrombin/go-module-router/v2/pkg/router"
	"github.com/mirkobrombin/go-warp/v1/cache"
	"github.com/vanilla-os/eratosthenes/internal/assets"
	"github.com/vanilla-os/eratosthenes/internal/config"
	"github.com/vanilla-os/eratosthenes/internal/db"
	"github.com/vanilla-os/eratosthenes/internal/indexer"
	"github.com/vanilla-os/eratosthenes/internal/models"
	"github.com/vanilla-os/eratosthenes/internal/modules/web"
)

func (c *ServeCmd) Run() error {
	config.Load()
	if c.Port != 0 && c.Port != 6001 {
		config.Instance.Port = c.Port
	}

	db.InitDB()
	defer db.Close()

	Eratosthenes.Log.Info("Initialized Database")

	cch := cache.NewInMemory[models.Package](
		cache.WithMaxEntries[models.Package](10000),
	)

	r := router.New()
	mux := r.HTTP.Mux()

	home := &web.HomeEndpoint{}
	search := &web.SearchEndpoint{}
	pkg := &web.PackageEndpoint{Cache: cch}

	mux.Handle("GET /", wrap(home))
	mux.Handle("GET /search", wrap(search))
	mux.Handle("GET /package/{name}", wrap(pkg))

	staticFS, err := fs.Sub(assets.Content, "static")
	if err != nil {
		Eratosthenes.Log.Errorf("Failed to subtree static assets: %v", err)
	} else {
		fileServer := http.FileServer(http.FS(staticFS))
		mux.Handle("GET /static/", http.StripPrefix("/static/", fileServer))
	}

	addr := fmt.Sprintf(":%d", config.Instance.Port)
	Eratosthenes.Log.Infof("Starting server on %s", addr)
	return r.Listen(addr)
}

func wrap(h interface {
	Handle(context.Context) (any, error)
}) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ctx := r.Context()
		ctx = context.WithValue(ctx, router.CtxKeyRequest, r)
		ctx = context.WithValue(ctx, router.CtxKeyResponseWriter, w)

		_, err := h.Handle(ctx)
		if err != nil {
			Eratosthenes.Log.Errorf("Error handling request: %v", err)
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		}
	}
}

func (c *IndexCmd) Run() error {
	config.Load()
	Eratosthenes.Log.Info("Starting indexer...")

	db.InitDB()
	defer db.Close()

	idx := indexer.NewIndexer(Eratosthenes.Log)
	idx.Index()

	Eratosthenes.Log.Info("Indexing completed successfully.")
	return nil
}
