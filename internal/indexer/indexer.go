package indexer

import (
	"bufio"
	"compress/gzip"
	"context"
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/ulikunitz/xz"
	"github.com/vanilla-os/eratosthenes/internal/config"
	"github.com/vanilla-os/eratosthenes/internal/db"
	"github.com/vanilla-os/eratosthenes/internal/models"
)

type Logger interface {
	Info(msg string)
	Infof(format string, args ...any)
	Error(msg string)
	Errorf(format string, args ...any)
}

type Indexer struct {
	logger Logger
}

func NewIndexer(l Logger) *Indexer {
	return &Indexer{logger: l}
}

func (i *Indexer) Cleanup() {
	i.logger.Info("Note: Cleanup for Slipstream involves overwriting keys. Obsolete keys might persist until compaction/expiry.")
}

func (i *Indexer) Index() {
	for branch, baseUrl := range config.Instance.Branches {
		for _, component := range config.Instance.RepoComponents {
			for _, arch := range config.Instance.Archs {
				url := strings.Replace(baseUrl, "@", component, 1)
				url = strings.Replace(url, "@", fmt.Sprintf("binary-%s", arch), 1)

				i.logger.Infof("Indexing branch '%s' component '%s' arch '%s' at %s", branch, component, arch, url)

				var content string
				var err error

				for _, ext := range []string{"", ".gz", ".xz"} {
					content, err = i.fetch(url + ext)
					if err == nil {
						break
					}
					if ext == ".xz" {
						i.logger.Infof("Error fetching %s: %v", url+ext, err)
					}
				}

				if content == "" {
					i.logger.Infof("Could not find Packages for %s/%s/%s", branch, component, arch)
					continue
				}

				i.parseAndInsert(content, branch, arch)
			}
		}
	}
}

func (i *Indexer) fetch(url string) (string, error) {
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("status code %d", resp.StatusCode)
	}

	var reader io.Reader = resp.Body

	if strings.HasSuffix(url, ".gz") {
		gzReader, err := gzip.NewReader(resp.Body)
		if err != nil {
			return "", err
		}
		defer gzReader.Close()
		reader = gzReader
	} else if strings.HasSuffix(url, ".xz") {
		xzReader, err := xz.NewReader(resp.Body)
		if err != nil {
			return "", err
		}
		reader = xzReader
	}

	bytes, err := io.ReadAll(reader)
	if err != nil {
		return "", err
	}

	return string(bytes), nil
}

func (i *Indexer) parseAndInsert(content, branch, arch string) {
	chunks := strings.Split(content, "\n\n")
	ctx := context.Background()

	tx, err := db.DB.Begin()
	if err != nil {
		i.logger.Errorf("Error starting transaction: %v", err)
		return
	}

	count := 0
	for _, chunk := range chunks {
		if strings.TrimSpace(chunk) == "" {
			continue
		}

		pkgMap := make(map[string]string)
		scanner := bufio.NewScanner(strings.NewReader(chunk))
		var currentKey string

		for scanner.Scan() {
			line := scanner.Text()
			if strings.HasPrefix(line, " ") {
				if currentKey != "" {
					pkgMap[currentKey] += "\n" + strings.TrimSpace(line)
				}
				continue
			}

			parts := strings.SplitN(line, ": ", 2)
			if len(parts) == 2 {
				currentKey = parts[0]
				pkgMap[currentKey] = parts[1]
			}
		}

		if _, ok := pkgMap["Package"]; !ok {
			continue
		}

		pkg := models.Package{
			Name:        pkgMap["Package"],
			Version:     pkgMap["Version"],
			Description: pkgMap["Description"],
			Section:     pkgMap["Section"],
			Homepage:    pkgMap["Homepage"],
			Maintainer:  pkgMap["Maintainer"],
			Depends:     pkgMap["Depends"],
			Recommends:  pkgMap["Recommends"],
			Suggests:    pkgMap["Suggests"],
			Conflicts:   pkgMap["Conflicts"],
			Replaces:    pkgMap["Replaces"],
			Provides:    pkgMap["Provides"],
			Filename:    pkgMap["Filename"],
			Branch:      branch,
			Arch:        arch,
		}

		key := fmt.Sprintf("%s|%s|%s", branch, arch, pkg.Name)

		if err := tx.Put(ctx, key, pkg, 0); err != nil {
			i.logger.Errorf("Error putting package %s: %v", pkg.Name, err)
		} else {
			count++
		}

		if count%1000 == 0 {
			if err := tx.Commit(ctx); err != nil {
				i.logger.Errorf("Error committing batch: %v", err)
			}
			tx, _ = db.DB.Begin()
		}
	}

	if err := tx.Commit(ctx); err != nil {
		i.logger.Errorf("Error committing final transaction: %v", err)
	}

	i.logger.Infof("Finished indexing %d packages for branch '%s' arch '%s'", count, branch, arch)
}
