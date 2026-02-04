# RxJS Subjects & Caching

## Subject Types

```typescript
import { Subject, BehaviorSubject, ReplaySubject, AsyncSubject } from 'rxjs';

export class SubjectExamples {
  // Subject: No initial value, only emits to future subscribers
  private clickSubject = new Subject<MouseEvent>();
  click$ = this.clickSubject.asObservable();

  onClick(event: MouseEvent) {
    this.clickSubject.next(event);
  }

  // BehaviorSubject: Has initial value, emits latest value to new subscribers
  private loadingSubject = new BehaviorSubject<boolean>(false);
  loading$ = this.loadingSubject.asObservable();

  setLoading(loading: boolean) {
    this.loadingSubject.next(loading);
  }

  // ReplaySubject: Replays N previous values to new subscribers
  private activitySubject = new ReplaySubject<Activity>(3); // Last 3 activities
  activity$ = this.activitySubject.asObservable();

  // AsyncSubject: Only emits last value when completed
  private finalResultSubject = new AsyncSubject<Result>();
  finalResult$ = this.finalResultSubject.asObservable();
}
```

## ShareReplay for Caching

```typescript
import { shareReplay } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class ConfigService {
  private http = inject(HttpClient);

  // Cache config, share with all subscribers
  config$ = this.http.get<Config>('/api/config').pipe(
    shareReplay({ bufferSize: 1, refCount: true })
  );

  // All components get same config without extra HTTP calls
  getConfig() {
    return this.config$;
  }
}
```
