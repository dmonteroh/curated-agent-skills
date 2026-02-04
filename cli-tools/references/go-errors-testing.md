# Go Error Handling & Testing

## Error Handling

```go
package main

import (
    "errors"
    "fmt"
    "os"
    "os/signal"
    "syscall"

    "github.com/spf13/cobra"
)

var deployCmd = &cobra.Command{
    Use:   "deploy",
    Short: "Deploy application",
    RunE: func(cmd *cobra.Command, args []string) error {
        if err := deploy(); err != nil {
            return handleError(err)
        }
        return nil
    },
}

func handleError(err error) error {
    switch {
    case errors.Is(err, os.ErrPermission):
        fmt.Fprintln(os.Stderr, "Permission denied")
        os.Exit(77)
    case errors.Is(err, os.ErrNotExist):
        fmt.Fprintf(os.Stderr, "File not found: %v\n", err)
        os.Exit(127)
    default:
        fmt.Fprintf(os.Stderr, "Deployment failed: %v\n", err)
        os.Exit(1)
    }
    return nil
}

func main() {
    c := make(chan os.Signal, 1)
    signal.Notify(c, os.Interrupt, syscall.SIGTERM)

    go func() {
        <-c
        fmt.Println("\nOperation cancelled")
        os.Exit(130)
    }()

    if err := deployCmd.Execute(); err != nil {
        os.Exit(1)
    }
}
```

## Testing

```go
package cmd

import (
    "bytes"
    "testing"

    "github.com/spf13/cobra"
    "github.com/stretchr/testify/assert"
)

func TestInitCommand(t *testing.T) {
    cmd := &cobra.Command{Use: "test"}
    cmd.AddCommand(initCmd)

    b := bytes.NewBufferString("")
    cmd.SetOut(b)
    cmd.SetArgs([]string{"init", "my-project"})

    err := cmd.Execute()
    assert.NoError(t, err)
    assert.Contains(t, b.String(), "Creating my-project")
}
```
