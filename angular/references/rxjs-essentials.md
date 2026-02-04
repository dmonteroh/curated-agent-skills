# RxJS Essentials

## Essential Operators

```typescript
import { Component, inject, signal } from '@angular/core';
import {
  map, filter, switchMap, catchError,
  debounceTime, distinctUntilChanged,
  tap, shareReplay, takeUntil
} from 'rxjs/operators';
import { Subject, of, EMPTY } from 'rxjs';

@Component({
  selector: 'app-search',
  standalone: true
})
export class SearchComponent {
  private searchService = inject(SearchService);
  private destroy$ = new Subject<void>();

  searchTerm$ = new Subject<string>();
  results = signal<SearchResult[]>([]);

  ngOnInit() {
    this.searchTerm$.pipe(
      debounceTime(300),              // Wait 300ms after typing
      distinctUntilChanged(),         // Only if value changed
      filter(term => term.length > 2), // Minimum 3 characters
      tap(() => this.loading.set(true)),
      switchMap(term =>               // Cancel previous requests
        this.searchService.search(term).pipe(
          catchError(err => {
            console.error(err);
            return of([]);            // Return empty on error
          })
        )
      ),
      tap(() => this.loading.set(false)),
      takeUntil(this.destroy$)        // Auto-unsubscribe
    ).subscribe(results => this.results.set(results));
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

## Higher-Order Operators

```typescript
import { switchMap, mergeMap, concatMap, exhaustMap } from 'rxjs/operators';

export class HigherOrderExamples {
  private http = inject(HttpClient);

  // switchMap: Cancel previous, use latest (search, typeahead)
  searchUsers(term$: Observable<string>) {
    return term$.pipe(
      switchMap(term => this.http.get<User[]>(`/api/users?q=${term}`))
    );
  }

  // mergeMap: Process all concurrently (independent requests)
  uploadFiles(files: File[]) {
    return from(files).pipe(
      mergeMap(file => this.http.post('/api/upload', file))
    );
  }

  // concatMap: Process sequentially (order matters)
  processQueue(tasks: Task[]) {
    return from(tasks).pipe(
      concatMap(task => this.http.post('/api/process', task))
    );
  }

  // exhaustMap: Ignore new until current completes (prevent double-click)
  saveForm(clicks$: Observable<void>, formData: any) {
    return clicks$.pipe(
      exhaustMap(() => this.http.post('/api/save', formData))
    );
  }
}
```

## Quick Reference

| Use Case | Operator |
|----------|----------|
| Transform values | `map`, `pluck` |
| Filter values | `filter`, `distinctUntilChanged` |
| Time-based | `debounceTime`, `throttleTime`, `delay` |
| Cancel previous | `switchMap` |
| Process all | `mergeMap` |
| Sequential | `concatMap` |
| Ignore new | `exhaustMap` |
| Combine latest | `combineLatest` |
| Wait for all | `forkJoin` |
| Error handling | `catchError`, `retry` |
| Cleanup | `takeUntilDestroyed`, `takeUntil` |
| Share result | `shareReplay` |
