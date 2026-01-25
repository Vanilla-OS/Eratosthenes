package web

import (
	"html/template"
	"log"
	"net/http"

	"github.com/vanilla-os/eratosthenes/internal/assets"
)

var baseTmpl *template.Template

func init() {
	var err error
	baseTmpl, err = template.New("base").ParseFS(assets.Content, "templates/base.html")
	if err != nil {
		log.Fatalf("Error validating base template: %v", err)
	}
}

func Render(w http.ResponseWriter, tmplPath string, data any) {
	tmpl, err := baseTmpl.Clone()
	if err != nil {
		log.Println("Error cloning template:", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	_, err = tmpl.ParseFS(assets.Content, tmplPath)
	if err != nil {
		log.Println("Error parsing template:", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	err = tmpl.ExecuteTemplate(w, "base", data)
	if err != nil {
		log.Println("Error executing template:", err)
	}
}

func ReadCookie(r *http.Request, name, defaultVal string) string {
	c, err := r.Cookie(name)
	if err != nil {
		return defaultVal
	}
	return c.Value
}
