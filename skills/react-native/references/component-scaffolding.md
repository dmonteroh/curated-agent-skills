# Component Scaffolding

Provides scaffolding guidance for React Native components with consistent structure, types, tests, styles, and a11y.

## Goals

- Predictable file layout
- Strong TypeScript contracts
- Platform-safe UI and accessibility
- Fast tests with React Native Testing Library

## Intake Checklist

- Component name and purpose
- Component type: `screen`, `layout`, `form`, `data-display`, `primitive`
- Props list with types and defaults
- State and side effects
- Styling approach: `StyleSheet` or `styled-components`
- Optional: navigation integration, analytics, feature flags

## Recommended File Layout

- `ComponentName.tsx`
- `ComponentName.styles.ts` or `ComponentName.styles.tsx` or none (inline StyleSheet)
- `ComponentName.test.tsx`
- `index.ts`

## TypeScript Contract

- Export a props interface with descriptions
- Prefer `React.ReactNode` for slot content
- Include `testID` when the component is used in E2E tests

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
  /** Test identifier for E2E */
  testID?: string;
}
```

## Component Template

```tsx
import * as React from "react";
import { Pressable, Text, View } from "react-native";

export interface ComponentNameProps {
  label: string;
  helperText?: string;
  disabled?: boolean;
  onAction?: () => void;
  testID?: string;
}

export function ComponentName({
  label,
  helperText,
  disabled = false,
  onAction,
  testID,
}: ComponentNameProps) {
  return (
    <View accessibilityLabel={`${label} container`} testID={testID}>
      <Text>{label}</Text>
      {helperText ? <Text>{helperText}</Text> : null}
      <Pressable
        accessibilityRole="button"
        accessibilityState={{ disabled }}
        disabled={disabled}
        onPress={onAction}
      >
        <Text>Action</Text>
      </Pressable>
    </View>
  );
}
```

## Styling Guidance

- Use `StyleSheet.create` for stable style objects
- Extract variants into small helpers
- Prefer `Pressable` over `TouchableOpacity`
- Use `SafeAreaView` at screen boundaries

## Accessibility Checklist

- Always set `accessibilityRole` on interactive elements
- Use `accessibilityState` for `disabled`, `selected`, `checked`
- Provide `accessibilityLabel` when the text label is not sufficient
- Ensure readable contrast and font sizes
- Support screen readers with clear labels

## Test Scaffold (RNTL)

```tsx
import { render, screen, fireEvent } from "@testing-library/react-native";
import { ComponentName } from "./ComponentName";

describe("ComponentName", () => {
  it("renders label", () => {
    render(<ComponentName label="Example" />);
    expect(screen.getByText("Example")).toBeTruthy();
  });

  it("calls onAction", () => {
    const onAction = jest.fn();
    render(<ComponentName label="Example" onAction={onAction} />);
    fireEvent.press(screen.getByText("Action"));
    expect(onAction).toHaveBeenCalledTimes(1);
  });
});
```

## Export Pattern

```ts
export { ComponentName } from "./ComponentName";
export type { ComponentNameProps } from "./ComponentName";
```
