# Application Profiling: Go and Java

Use this reference for Go and Java profiling workflows, including CPU, memory, and allocation analysis.

## Go Profiling

### pprof

```go
import (
    "net/http"
    _ "net/http/pprof"
    "runtime"
)

func main() {
    // Enable profiling endpoint
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()

    // Your application code
}
```

```bash
# CPU profile
curl http://localhost:6060/debug/pprof/profile?seconds=30 > cpu.prof
go tool pprof cpu.prof

# Memory profile
curl http://localhost:6060/debug/pprof/heap > heap.prof
go tool pprof heap.prof

# Goroutine profile
curl http://localhost:6060/debug/pprof/goroutine > goroutine.prof
go tool pprof goroutine.prof

# Web interface
go tool pprof -http=:8080 cpu.prof
```

## Java Profiling

### VisualVM

```bash
# Start application with JMX
java -Dcom.sun.management.jmxremote \
     -Dcom.sun.management.jmxremote.port=9010 \
     -Dcom.sun.management.jmxremote.authenticate=false \
     -Dcom.sun.management.jmxremote.ssl=false \
     -jar app.jar

# Connect with VisualVM
jvisualvm
```

### async-profiler

```bash
# CPU profiling
./profiler.sh -d 30 -f cpu.html <pid>

# Allocation profiling
./profiler.sh -d 30 -e alloc -f alloc.html <pid>

# Flame graph
./profiler.sh -d 30 -f flamegraph.svg <pid>
```
