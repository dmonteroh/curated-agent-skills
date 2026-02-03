# React Native Best Practices (Condensed)

## Core Rendering (Critical)

- Never use `{value && <Component />}` when `value` can be `""` or `0`.
- Wrap all strings in `<Text>` components.

```tsx
{count ? <Text>{count} items</Text> : null}
```

## List Performance (High)

- Avoid inline objects in `renderItem`.
- Hoist callbacks to list root.
- Keep list items lightweight (no queries, minimal hooks).
- Use a virtualizer (`FlashList`, `LegendList`) for any list.
- Pass primitives to list items for stable memoization.

## Animation (High)

- Animate `transform` and `opacity`, not layout properties.
- Prefer `useDerivedValue` over `useAnimatedReaction` when possible.
- For press animations, use `GestureDetector` + Reanimated shared values.

## Scroll Performance (High)

- Never track scroll position in `useState` (use Reanimated or refs).

## Navigation (High)

- Prefer native navigators when available.

## React State (Medium)

- Minimize state variables; derive values during render.
- Use functional updaters when state depends on previous value.
- Use fallback state when possible instead of redundant initial state.

## UI and UX (Medium)

- Use `Pressable` (not `TouchableOpacity`).
- Prefer `expo-image` for optimized images.
- Use native menus and modals where possible.
- Use `contentInsetAdjustmentBehavior` and `contentInset` for safe areas.

## Design System (Medium)

- Prefer compound components to polymorphic children for text + icon UI.

## Monorepo (Low)

- Install native deps in the app package (for autolinking).
- Keep single versions of native deps across packages.

## JavaScript (Low)

- Hoist `Intl.*` formatter creation to module scope.

## Fonts (Low)

- Use Expo font config plugin to embed fonts at build time.
