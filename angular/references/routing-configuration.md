# Router Configuration and Lazy Loading

## Routes configuration

```typescript
// app.routes.ts
import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/home',
    pathMatch: 'full'
  },
  {
    path: 'home',
    component: HomeComponent,
    title: 'Home'
  },
  {
    path: 'users',
    loadComponent: () => import('./users/users.component').then(m => m.UsersComponent),
    title: 'Users'
  },
  {
    path: 'users/:id',
    loadComponent: () => import('./users/user-detail.component').then(m => m.UserDetailComponent),
    canActivate: [authGuard],
    resolve: { user: userResolver }
  },
  {
    path: '**',
    loadComponent: () => import('./not-found/not-found.component').then(m => m.NotFoundComponent),
    title: '404 Not Found'
  }
];

// app.config.ts
import { provideRouter, withComponentInputBinding, withPreloading } from '@angular/router';
import { PreloadAllModules } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withComponentInputBinding(),
      withPreloading(PreloadAllModules)
    )
  ]
};
```

## Lazy loading feature routes

```typescript
// admin/admin.routes.ts
import { Routes } from '@angular/router';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./admin-dashboard.component').then(m => m.AdminDashboardComponent)
  },
  {
    path: 'users',
    loadComponent: () => import('./admin-users.component').then(m => m.AdminUsersComponent)
  },
  {
    path: 'settings',
    loadComponent: () => import('./admin-settings.component').then(m => m.AdminSettingsComponent)
  }
];
```

## Custom preloading strategy

```typescript
import { Injectable } from '@angular/core';
import { PreloadingStrategy, Route } from '@angular/router';
import { Observable, of, timer } from 'rxjs';
import { mergeMap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class CustomPreloadingStrategy implements PreloadingStrategy {
  preload(route: Route, load: () => Observable<any>): Observable<any> {
    if (route.data?.['preload']) {
      const delay = route.data?.['preloadDelay'] || 0;
      return timer(delay).pipe(
        mergeMap(() => load())
      );
    }
    return of(null);
  }
}

const routes: Routes = [
  {
    path: 'important',
    loadChildren: () => import('./important/important.routes'),
    data: { preload: true, preloadDelay: 2000 }
  }
];

provideRouter(routes, withPreloading(CustomPreloadingStrategy));
```
