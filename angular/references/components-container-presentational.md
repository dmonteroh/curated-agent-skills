# Container and Presentational Components

## Smart vs. dumb component split

```typescript
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
