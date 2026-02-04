# Signal Inputs, Outputs, and Models

## Input/output with signals

```typescript
import { Component, input, model, output } from '@angular/core';

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
  placeholder = input<string>('Search...');
  initialQuery = input<string>('');

  queryChange = output<string>();

  query = model<string>('');

  onQueryChange(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    this.query.set(value);
    this.queryChange.emit(value);
  }
}

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
