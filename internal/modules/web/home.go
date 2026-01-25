package web

import (
	"context"
	"net/http"

	"github.com/mirkobrombin/go-module-router/v2/pkg/core"
	"github.com/mirkobrombin/go-module-router/v2/pkg/router"
	"github.com/vanilla-os/eratosthenes/internal/config"
)

type HomeEndpoint struct {
	Meta core.Pattern `method:"GET" path:"/"`
}

func (e *HomeEndpoint) Handle(ctx context.Context) (any, error) {
	w, ok := ctx.Value(router.CtxKeyResponseWriter).(http.ResponseWriter)
	if !ok {
		return nil, nil
	}
	r, ok := ctx.Value(router.CtxKeyRequest).(*http.Request)
	if !ok {
		return nil, nil
	}

	branch := ReadCookie(r, "branch", "main")
	arch := ReadCookie(r, "arch", "amd64")

	data := map[string]any{
		"Branch":        branch,
		"CurrentArch":   arch,
		"Archs":         config.Instance.Archs,
		"ShowSearchBar": false,
	}

	Render(w, "templates/index.html", data)
	return nil, nil
}
