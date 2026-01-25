package main

import (
	"fmt"
	"os"

	"github.com/vanilla-os/eratosthenes/internal/cli"
	"github.com/vanilla-os/sdk/pkg/v1/app"
	"github.com/vanilla-os/sdk/pkg/v1/app/types"
)

var Version = "development"

func main() {
	var err error

	cli.Eratosthenes, err = app.NewApp(types.AppOptions{
		Name:    "eratosthenes",
		Version: Version,
		RDNN:    "org.vanillaos.eratosthenes",
	})
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	rootCmdStruct := &cli.RootCmd{
		Version: Version,
	}

	err = cli.Eratosthenes.WithCLI(rootCmdStruct)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	cli.Eratosthenes.CLI.SetName("eratosthenes")

	err = cli.Eratosthenes.CLI.Execute()
	if err != nil {
		cli.Eratosthenes.Log.Error(err.Error())
		os.Exit(1)
	}
}
