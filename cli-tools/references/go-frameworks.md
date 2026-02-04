# Go CLI Frameworks

## Cobra (Recommended)

```go
// cmd/root.go
package cmd

import (
    "fmt"
    "os"

    "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
    Use:     "mycli",
    Short:   "My awesome CLI tool",
    Version: "1.0.0",
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

// cmd/init.go
package cmd

import "github.com/spf13/cobra"

var initCmd = &cobra.Command{
    Use:   "init [name]",
    Short: "Initialize a new project",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        return initProject(args[0])
    },
}

func init() {
    rootCmd.AddCommand(initCmd)
    initCmd.Flags().StringP("template", "t", "default", "Project template")
    initCmd.Flags().BoolP("force", "f", false, "Overwrite existing")
}
```
