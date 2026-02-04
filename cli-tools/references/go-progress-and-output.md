# Go Progress & Output

## Progress Indicators

```go
package main

import (
    "time"

    "github.com/schollz/progressbar/v3"
)

func main() {
    bar := progressbar.Default(100, "Downloading")
    for i := 0; i < 100; i++ {
        bar.Add(1)
        time.Sleep(40 * time.Millisecond)
    }
}
```

## Spinner

```go
package main

import (
    "fmt"
    "time"

    "github.com/briandowns/spinner"
)

func main() {
    s := spinner.New(spinner.CharSets[11], 100*time.Millisecond)
    s.Suffix = " Installing dependencies..."
    s.Start()

    time.Sleep(4 * time.Second)

    s.UpdateCharSet(spinner.CharSets[9])
    s.Suffix = " Processing..."
    time.Sleep(2 * time.Second)

    s.Stop()
    fmt.Println("✓ Done!")
}
```

## Colored Output

```go
package main

import "github.com/fatih/color"

func main() {
    color.Blue("Info: Starting deployment...")
    color.Green("Success: Deployment complete!")
    color.Yellow("Warning: Deprecated flag used")
    color.Red("Error: Deployment failed")

    success := color.New(color.FgGreen, color.Bold).PrintlnFunc()
    error := color.New(color.FgRed, color.Bold).PrintlnFunc()

    success("✓ Build successful")
    error("✗ Build failed")

    color.Cyan("Processing %d files...\n", 42)
}
```
