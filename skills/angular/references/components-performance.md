# Component Performance Reference

## Performance: OnPush & TrackBy

```typescript
@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    @for (product of products(); track trackByProductId($index, product)) {
      <app-product-card [product]="product" />
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ProductListComponent {
  products = input.required<Product[]>();

  // TrackBy for optimal rendering
  trackByProductId(index: number, product: Product): number {
    return product.id;
  }
}
```

## Quick Reference

| Pattern | Angular 17+ Approach |
|---------|---------------------|
| Component | Standalone by default |
| State | Signals (`signal()`, `computed()`) |
| Input | `input()`, `input.required()` |
| Output | `output<T>()` |
| Two-way | `model<T>()` |
| DI | `inject()` function |
| Control Flow | `@if`, `@for`, `@switch` |
| Change Detection | `ChangeDetectionStrategy.OnPush` |
