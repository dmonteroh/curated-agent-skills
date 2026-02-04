---
name: react-native
description: "Build cross-platform mobile apps with React Native/Expo: navigation, platform handling (iOS/Android), performance (FlatList), storage, and native module integration. Not for React web or Next.js."
category: frontend
---

# React Native Pro

This skill is for React Native and Expo apps.

## Use this skill when

- Building React Native features/components
- Implementing navigation (Expo Router / React Navigation)
- Handling platform-specific behavior (safe areas, keyboard, back button)
- Optimizing list and rendering performance (FlatList/SectionList)
- Managing mobile persistence (AsyncStorage/MMKV) and app lifecycle

### Trigger phrases

- "React Native" or "Expo" mobile app changes
- "FlatList performance" or "scrolling lag" on mobile
- "Safe area", "keyboard avoiding", or "Android back button"
- "AsyncStorage", "MMKV", or "app state" persistence

## Do not use this skill when

- The project is React web or Next.js only
- The request is for native iOS/Android-only code without React Native
- The task is purely backend or API work

## Workflow (Deterministic)

1. Confirm runtime (Expo managed vs bare RN), target platforms, and navigation approach.
   - Decision: if Expo managed, prefer Expo APIs; if bare RN, confirm native module availability.
   - Output: a short plan stating runtime, platforms, and navigation library.
2. Implement UI with platform-safe primitives and predictable layout.
   - Output: component/screen changes with layout constraints noted (SafeArea, KeyboardAvoidingView, flex rules).
3. Handle platform-specific behavior explicitly (SafeArea, keyboard, Android back).
   - Decision: if platform divergence is needed, use `Platform.OS` or platform-specific files.
   - Output: platform handling notes and any conditional logic added.
4. Treat lists as a performance surface (memoized row, stable keys, FlatList tuning).
   - Output: list optimization summary (props tuned, memoization strategy, key strategy).
5. Verify expected behavior on target platforms.
   - Output: device/simulator matrix and manual checks performed or requested.

## Common pitfalls

- Forgetting `SafeAreaView` or `KeyboardAvoidingView` for critical layouts
- Unstable keys or inline render functions in `FlatList`
- Platform-specific behavior hidden behind implicit assumptions
- Storage writes on every render or without hydration checks

## Example prompt

"Improve scrolling performance in our React Native FlatList screen and make sure it respects safe areas."

## Output Contract (Always)

- Report using this format:
  - Changes: brief summary of components/screens touched
  - Platform handling: iOS/Android differences and guards
  - Navigation: routes/params updates if applicable
  - Performance: list/image tuning applied
  - Verification: device/simulator coverage and checks run

## References (Optional)

- Index: `references/README.md`
- Navigation: `references/expo-router.md`
- Platform handling: `references/platform-handling.md`
- List optimization: `references/list-optimization.md`
- Storage hooks: `references/storage-hooks.md`
- Component scaffolding: `references/component-scaffolding.md`
- Architecture: `references/architecture.md`
- Best practices: `references/best-practices.md`
- Project structure: `references/project-structure.md`
