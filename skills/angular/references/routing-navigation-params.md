# Navigation, Params, and Router Events

## Route parameters and navigation

```typescript
import { Component, inject, input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-product-detail',
  standalone: true
})
export class ProductDetailComponent {
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  id = input.required<string>();

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      this.loadProduct(id);
    });

    this.route.queryParamMap.subscribe(params => {
      const filter = params.get('filter');
      const sort = params.get('sort');
    });
  }

  goToEdit() {
    this.router.navigate(['/products', this.id(), 'edit']);
  }

  applyFilter(filter: string) {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { filter },
      queryParamsHandling: 'merge'
    });
  }
}
```

## Router events

```typescript
import { Component, inject, signal } from '@angular/core';
import { Router, NavigationEnd, NavigationError, NavigationStart } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true
})
export class AppComponent {
  private router = inject(Router);
  loading = signal(false);

  constructor() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationStart)
    ).subscribe(() => {
      this.loading.set(true);
    });

    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.loading.set(false);
    });

    this.router.events.pipe(
      filter(event => event instanceof NavigationError)
    ).subscribe((event: NavigationError) => {
      console.error('Navigation error:', event.error);
      this.loading.set(false);
    });
  }
}
```

## Child routes and outlets

```typescript
const routes: Routes = [
  {
    path: 'dashboard',
    component: DashboardComponent,
    children: [
      {
        path: 'stats',
        component: StatsComponent,
        outlet: 'panel'
      },
      {
        path: 'charts',
        component: ChartsComponent,
        outlet: 'panel'
      }
    ]
  }
];

@Component({
  template: `
    <div class="dashboard">
      <div class="main">
        <router-outlet></router-outlet>
      </div>
      <div class="panel">
        <router-outlet name="panel"></router-outlet>
      </div>
    </div>
  `
})
export class DashboardComponent {}

this.router.navigate(['/dashboard', { outlets: { panel: ['stats'] } }]);
```
