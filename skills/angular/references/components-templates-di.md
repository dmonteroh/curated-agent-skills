# Templates, Projection, and DI

## Content Projection

```typescript
// Card component with multiple slots
@Component({
  selector: 'app-card',
  standalone: true,
  template: `
    <div class="card">
      <div class="card-header">
        <ng-content select="[header]"></ng-content>
      </div>
      <div class="card-body">
        <ng-content></ng-content>
      </div>
      <div class="card-footer">
        <ng-content select="[footer]"></ng-content>
      </div>
    </div>
  `
})
export class CardComponent {}

// Usage
@Component({
  template: `
    <app-card>
      <h2 header>Card Title</h2>
      <p>Card content goes here</p>
      <button footer>Action</button>
    </app-card>
  `
})
export class ParentComponent {}
```

## Dependency Injection

```typescript
import { Component, inject } from '@angular/core';
import { UserService } from './user.service';

@Component({
  selector: 'app-user-dashboard',
  standalone: true
})
export class UserDashboardComponent {
  // Modern inject() API
  private userService = inject(UserService);
  private router = inject(Router);

  // Optional dependency
  private logger = inject(LoggerService, { optional: true });

  users = signal<User[]>([]);

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.userService.getUsers().subscribe({
      next: users => this.users.set(users),
      error: err => this.logger?.error('Failed to load users', err)
    });
  }
}
```

## New Control Flow (@if, @for)

```typescript
@Component({
  template: `
    <!-- @if instead of *ngIf -->
    @if (user(); as currentUser) {
      <div>Hello, {{ currentUser.name }}</div>
    } @else if (loading()) {
      <div>Loading...</div>
    } @else {
      <div>Please log in</div>
    }

    <!-- @for instead of *ngFor -->
    @for (item of items(); track item.id) {
      <div>{{ item.name }}</div>
    } @empty {
      <div>No items found</div>
    }

    <!-- @switch instead of *ngSwitch -->
    @switch (status()) {
      @case ('pending') {
        <span>Pending...</span>
      }
      @case ('success') {
        <span>Success!</span>
      }
      @default {
        <span>Unknown</span>
      }
    }
  `
})
export class ModernControlFlowComponent {
  user = signal<User | null>(null);
  loading = signal(false);
  items = signal<Item[]>([]);
  status = signal<'pending' | 'success' | 'error'>('pending');
}
```
