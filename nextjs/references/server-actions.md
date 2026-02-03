# Server Actions

## Basic Action

```tsx
'use server'

import { revalidatePath } from "next/cache"

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string
  const content = formData.get("content") as string
  await db.post.create({ data: { title, content } })
  revalidatePath("/posts")
}
```

## Form Usage

```tsx
import { createPost } from "@/app/actions"

export default function NewPost() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit">Create</button>
    </form>
  )
}
```

## Validation Pattern

```tsx
'use server'

import { z } from "zod"

const Schema = z.object({
  title: z.string().min(3).max(100),
  content: z.string().min(10),
})

export async function createPost(formData: FormData) {
  const result = Schema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
  })

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors }
  }

  await db.post.create({ data: result.data })
  revalidatePath("/posts")
  return { success: true }
}
```

## Client Form with useFormState

```tsx
'use client'

import { useFormState, useFormStatus } from "react-dom"
import { createPost } from "@/app/actions"

const initialState = { errors: {} }

function SubmitButton() {
  const { pending } = useFormStatus()
  return <button disabled={pending}>{pending ? "Saving" : "Save"}</button>
}

export function CreatePostForm() {
  const [state, formAction] = useFormState(createPost, initialState)

  return (
    <form action={formAction}>
      <input name="title" />
      {state.errors?.title && <p>{state.errors.title[0]}</p>}
      <textarea name="content" />
      <SubmitButton />
    </form>
  )
}
```

## Best Practices

- Validate inputs (Zod/TypeBox).
- Auth check before mutations.
- Return error objects instead of throwing.
- Revalidate paths/tags after mutations.
- Use `useOptimistic` for better UX when appropriate.
