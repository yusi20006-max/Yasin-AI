// cmd/fetch/main.go
//
// Minimal CLI entry point for FeedBridge's vendored fetcher.
// Unlike OpenFeed's original cmd/server (which ran an HTTP server for
// the PWA), this just fetches one channel and prints JSON to stdout,
// so Python's Fetch Engine can invoke it as a subprocess:
//
//	./fetch <channel_username>
package main

import (
	"encoding/json"
	"fmt"
	"os"

	"feedbridge/fetcher/parser"
	"feedbridge/fetcher/provider"
	"feedbridge/fetcher/telemirror"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: fetch <channel_username>")
		os.Exit(1)
	}
	name := os.Args[1]

	html, err := provider.Default.LoadChannel(name)
	if err != nil {
		fmt.Fprintln(os.Stderr, "fetch error:", err)
		os.Exit(1)
	}

	ch, posts, err := telemirror.ParseHTML(string(html))
	if err != nil {
		fmt.Fprintln(os.Stderr, "parse error:", err)
		os.Exit(1)
	}

	channel := parser.Convert(ch, posts)

	enc := json.NewEncoder(os.Stdout)
	if err := enc.Encode(channel); err != nil {
		fmt.Fprintln(os.Stderr, "encode error:", err)
		os.Exit(1)
	}
}
