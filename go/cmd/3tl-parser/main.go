package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/jiriknesl/3tl/pkg/parser"
)

func main() {
	prettyFlag := flag.Bool("pretty", false, "Pretty-print JSON output")
	flag.Parse()

	args := flag.Args()
	if len(args) != 1 {
		fmt.Fprintf(os.Stderr, "Usage: %s [--pretty] <file.3tl>\n", os.Args[0])
		os.Exit(1)
	}

	filename := args[0]

	// Parse the file
	doc, err := parser.ParseFile(filename)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing file: %v\n", err)
		os.Exit(1)
	}

	// Output JSON
	if err := parser.WriteJSON(os.Stdout, doc, *prettyFlag); err != nil {
		fmt.Fprintf(os.Stderr, "Error writing JSON: %v\n", err)
		os.Exit(1)
	}

	fmt.Println() // Add newline at end
}
