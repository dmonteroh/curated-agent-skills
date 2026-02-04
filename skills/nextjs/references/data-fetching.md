# Data Fetching & Caching

## Fetch Cache Options

```tsx
fetch(url, { cache: "force-cache" }) // SSG
fetch(url, { cache: "no-store" }) // SSR
fetch(url, { next: { revalidate: 60 } }) // ISR
fetch(url, { next: { tags: ["products"] } }) // Tag-based
```

## Route Segment Config

```tsx
export const dynamic = "force-dynamic" // or "force-static"
export const revalidate = 3600
export const fetchCache = "default-cache"
export const runtime = "nodejs" // or "edge"
export const preferredRegion = "auto"
```

## Parallel vs Sequential Fetching

```tsx
const [user, posts] = await Promise.all([getUser(), getPosts()])

const user = await getUser()
const posts = await getPostsFor(user.id)
```

## React cache() for Deduplication

```tsx
import { cache } from "react"

export const getUser = cache(async (id: string) => {
  const res = await fetch(`/api/users/${id}`)
  return res.json()
})
```

## On-Demand Revalidation

```tsx
import { revalidatePath, revalidateTag } from "next/cache"

export async function updateProduct(id: string, data: ProductData) {
  await db.product.update({ where: { id }, data })
  revalidateTag("products")
  revalidatePath(`/products/${id}`)
}
```

## Streaming with Suspense

```tsx
import { Suspense } from "react"

export default function Page() {
  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        <SlowSection />
      </Suspense>
    </div>
  )
}
```

## Best Practices

- Default to cached fetches unless data must be real-time.
- Use ISR for semi-dynamic content.
- Use tags for granular invalidation.
- Fetch in parallel when independent.
- Use Suspense to stream slow sections.
