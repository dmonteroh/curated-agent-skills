# Guards and Resolvers

## Functional guards

```typescript
// guards/auth.guard.ts
import { inject } from '@angular/core';
import { Router, CanActivateFn, CanDeactivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.hasRole('admin')) {
    return true;
  }

  return router.createUrlTree(['/unauthorized']);
};

export const canDeactivateGuard: CanDeactivateFn<FormComponent> = (component) => {
  if (component.hasUnsavedChanges()) {
    return confirm('You have unsaved changes. Are you sure you want to leave?');
  }
  return true;
};
```

## Guards that return observables

```typescript
export const dataGuard: CanActivateFn = (route, state) => {
  const dataService = inject(DataService);
  const router = inject(Router);

  return dataService.checkAccess(route.params['id']).pipe(
    map(hasAccess => {
      if (hasAccess) {
        return true;
      }
      return router.createUrlTree(['/no-access']);
    }),
    catchError(() => of(router.createUrlTree(['/error'])))
  );
};
```

## Resolvers

```typescript
// resolvers/user.resolver.ts
import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { catchError, of } from 'rxjs';
import { User } from '../models/user.model';
import { UsersService } from '../services/users.service';

export const userResolver: ResolveFn<User | null> = (route, state) => {
  const usersService = inject(UsersService);
  const id = route.paramMap.get('id')!;

  return usersService.getById(id).pipe(
    catchError(() => of(null))
  );
};

@Component({
  selector: 'app-user-detail',
  standalone: true,
  template: `
    @if (user) {
      <h1>{{ user.name }}</h1>
    } @else {
      <p>User not found</p>
    }
  `
})
export class UserDetailComponent {
  user = input<User | null>(null);
}
```
