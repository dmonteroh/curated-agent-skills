# RxJS Error Handling and Lifecycle

## Error handling patterns

```typescript
import { catchError, mergeMap, retryWhen } from 'rxjs/operators';
import { throwError, of, timer } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class DataService {
  private http = inject(HttpClient);

  getData() {
    return this.http.get<Data>('/api/data').pipe(
      retryWhen(errors =>
        errors.pipe(
          mergeMap((error, index) => {
            if (index >= 3) {
              return throwError(() => error);
            }
            const delayMs = Math.pow(2, index) * 1000;
            return timer(delayMs);
          })
        )
      ),
      catchError(err => {
        console.error('Failed after retries:', err);
        return of(null);
      })
    );
  }

  saveData(data: Data) {
    return this.http.post('/api/data', data).pipe(
      catchError(err => {
        if (err.status === 401) {
          return throwError(() => new Error('Unauthorized'));
        }
        return throwError(() => err);
      })
    );
  }
}
```

## Subscription lifecycle management

```typescript
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-auto-cleanup',
  standalone: true
})
export class AutoCleanupComponent {
  private dataService = inject(DataService);
  private destroyRef = inject(DestroyRef);

  data = signal<Data[]>([]);

  constructor() {
    this.dataService.getData().pipe(
      takeUntilDestroyed()
    ).subscribe(data => this.data.set(data));

    const subscription = this.dataService.getUpdates().subscribe();
    this.destroyRef.onDestroy(() => subscription.unsubscribe());
  }
}

@Component({
  selector: 'app-manual-cleanup',
  standalone: true
})
export class ManualCleanupComponent implements OnDestroy {
  private destroy$ = new Subject<void>();

  ngOnInit() {
    this.dataService.getData().pipe(
      takeUntil(this.destroy$)
    ).subscribe();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```
