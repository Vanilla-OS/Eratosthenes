package cli

import (
	"github.com/vanilla-os/sdk/pkg/v1/app"
	"github.com/vanilla-os/sdk/pkg/v1/cli"
)

var Eratosthenes *app.App

type RootCmd struct {
	cli.Base
	Version string
	Serve   ServeCmd `cmd:"serve" help:"Start the web server"`
	Index   IndexCmd `cmd:"index" help:"Index packages from repositories"`
}

type ServeCmd struct {
	cli.Base
	Port int `flag:"short:p, long:port, name:port, default:6001"`
}

type IndexCmd struct {
	cli.Base
}
