# Component Architecture & Signals

## Standalone Component Pattern

```typescript
import { Component, signal, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-profile.component.html',
  styleUrl: './user-profile.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserProfileComponent {
  // Signal-based state
  count = signal(0);
  doubleCount = computed(() => this.count() * 2);

  constructor() {
    // Side effects
    effect(() => {
      console.log(`Count is: ${this.count()}`);
    });
  }

  increment() {
    this.count.update(value => value + 1);
  }
}
```

## Input/Output with Signals

```typescript
import { Component, input, output, model } from '@angular/core';

@Component({
  selector: 'app-search-box',
  standalone: true,
  template: `
    <input
      [value]="query()"
      (input)="onQueryChange($event)"
      [placeholder]="placeholder()" />
  `
})
export class SearchBoxComponent {
  // Signal inputs (Angular 17.1+)
  placeholder = input<string>('Search...');
  initialQuery = input<string>('');

  // Signal outputs
  queryChange = output<string>();

  // Two-way binding with model signal
  query = model<string>('');

  onQueryChange(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    this.query.set(value);
    this.queryChange.emit(value);
  }
}

// Parent usage
@Component({
  template: `
    <app-search-box
      [(query)]="searchQuery"
      [placeholder]="'Find users...'"
      (queryChange)="onSearch($event)" />
  `
})
export class ParentComponent {
  searchQuery = signal('');

  onSearch(query: string) {
    console.log('Searching:', query);
  }
}
```

## Smart vs Dumb Components

```typescript
// Smart Component (Container)
@Component({
  selector: 'app-users-container',
  standalone: true,
  imports: [UserListComponent],
  template: `
    <app-user-list
      [users]="users()"
      [loading]="loading()"
      (userSelected)="onUserSelected($event)" />
  `
})
export class UsersContainerComponent {
  private usersService = inject(UsersService);

  users = signal<User[]>([]);
  loading = signal(true);

  constructor() {
    effect(() => {
      this.usersService.getUsers().subscribe({
        next: users => {
          this.users.set(users);
          this.loading.set(false);
        },
        error: err => console.error(err)
      });
    });
  }

  onUserSelected(user: User) {
    // Handle business logic
  }
}

// Dumb Component (Presentational)
@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (loading()) {
      <div>Loading...</div>
    } @else {
      @for (user of users(); track user.id) {
        <div (click)="userSelected.emit(user)">
          {{ user.name }}
        </div>
      }
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserListComponent {
  users = input.required<User[]>();
  loading = input<boolean>(false);
  userSelected = output<User>();
}
```
