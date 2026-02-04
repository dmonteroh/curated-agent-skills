# App Router Patterns

Provides file conventions, layouts, route groups, and advanced routing patterns.

## File Conventions

```
app/
├── layout.tsx       # Shared UI wrapper
├── page.tsx         # Route UI
├── loading.tsx      # Loading UI (Suspense)
├── error.tsx        # Error boundary
├── not-found.tsx    # 404 UI
├── route.ts         # API endpoint
├── template.tsx     # Re-mounted layout
├── default.tsx      # Parallel route fallback
└── opengraph-image.tsx  # OG image generation
```

## Route Groups and Layouts

```
app/
├── (marketing)/
│   ├── layout.tsx
│   └── about/page.tsx
└── (app)/
    ├── layout.tsx
    └── dashboard/page.tsx
```

Layouts persist across routes. Templates re-mount on navigation.

## Parallel Routes

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({ children, analytics, team }: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <div className="dashboard-grid">
      <main>{children}</main>
      <aside>{analytics}</aside>
      <aside>{team}</aside>
    </div>
  )
}
```

## Intercepting Routes (Modal Pattern)

```
app/
├── @modal/
│   ├── (.)photos/[id]/page.tsx
│   └── default.tsx
├── photos/[id]/page.tsx
└── layout.tsx
```

Intercepting routes show a modal on in-app navigation and a full page on direct load.

## Metadata API

```tsx
import type { Metadata } from "next"

export async function generateMetadata(
  { params }: { params: { slug: string } }
): Promise<Metadata> {
  const product = await getProduct(params.slug)
  if (!product) return {}

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [{ url: product.image, width: 1200, height: 630 }],
    },
  }
}
```
