# Component Scaffolding

Use this when you need to generate a new React component with consistent structure, types, tests, styles, and docs.

## Goals

- Predictable files and exports
- Strong TypeScript contracts
- Accessible UI by default
- Fast tests with React Testing Library
- Styling that matches the project approach

## Intake Checklist

- Component name and purpose
- Component type: `page`, `layout`, `form`, `data-display`, `primitive`
- Props list with types and defaults
- State and side effects
- Styling approach: `css-modules`, `styled-components`, `tailwind`
- Optional: storybook, i18n, analytics, feature flags

## Recommended File Layout

- `ComponentName.tsx`
- `ComponentName.module.css` or `ComponentName.styles.ts` or none (tailwind)
- `ComponentName.test.tsx`
- `ComponentName.stories.tsx` (optional)
- `index.ts`

## TypeScript Contract

- Export a props interface with descriptions
- Keep props flat and stable
- Prefer `React.ReactNode` for slot content
- Use `aria-*` and `data-*` pass-through as needed

Example props interface:

```tsx
export interface ComponentNameProps {
  /** Visual label for the component */
  label: string;
  /** Optional helper content */
  helperText?: string;
  /** Disabled state */
  disabled?: boolean;
  /** Called on primary action */
  onAction?: () => void;
  /** Custom className hook */
  className?: string;
}
```

## Component Template

```tsx
import * as React from "react";

export interface ComponentNameProps {
  label: string;
  helperText?: string;
  disabled?: boolean;
  onAction?: () => void;
  className?: string;
}

export function ComponentName({
  label,
  helperText,
  disabled = false,
  onAction,
  className,
}: ComponentNameProps) {
  return (
    <div className={className} aria-disabled={disabled}>
      <div>{label}</div>
      {helperText ? <div>{helperText}</div> : null}
      <button type="button" onClick={onAction} disabled={disabled}>
        Action
      </button>
    </div>
  );
}
```

## Styling Guidance

- `css-modules`: `import styles from "./ComponentName.module.css";` and apply `className={styles.root}`
- `styled-components`: export styled primitives from `ComponentName.styles.ts`
- `tailwind`: prefer `clsx` and a `className` prop for overrides

## Accessibility Checklist

- Use semantic elements before `div`
- Provide `aria-label` when visible text is not available
- Keep focus states visible
- Respect `disabled` and `aria-disabled`
- Ensure keyboard navigation works end-to-end

## Test Scaffold (RTL)

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ComponentName } from "./ComponentName";

describe("ComponentName", () => {
  it("renders label", () => {
    render(<ComponentName label="Example" />);
    expect(screen.getByText("Example")).toBeInTheDocument();
  });

  it("calls onAction", () => {
    const onAction = jest.fn();
    render(<ComponentName label="Example" onAction={onAction} />);
    userEvent.click(screen.getByRole("button", { name: "Action" }));
    expect(onAction).toHaveBeenCalledTimes(1);
  });
});
```

## Accessibility Test (Optional)

```tsx
import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import { ComponentName } from "./ComponentName";

it("has no a11y violations", async () => {
  const { container } = render(<ComponentName label="Example" />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Export Pattern

```ts
export { ComponentName } from "./ComponentName";
export type { ComponentNameProps } from "./ComponentName";
```

## Storybook Scaffold (Optional)

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { ComponentName } from "./ComponentName";

const meta: Meta<typeof ComponentName> = {
  title: "Components/ComponentName",
  component: ComponentName,
};

export default meta;

type Story = StoryObj<typeof ComponentName>;

export const Default: Story = {
  args: { label: "Example" },
};
```
