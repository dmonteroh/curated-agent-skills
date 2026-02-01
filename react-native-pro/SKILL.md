---
name: react-native-pro
description: "Build cross-platform mobile apps with React Native/Expo: navigation, platform handling (iOS/Android), performance (FlatList), storage, and native module integration. Not for React web or Next.js."
---

# React Native Pro

This skill is for React Native and Expo apps.

## Use this skill when

- Building React Native features/components
- Implementing navigation (Expo Router / React Navigation)
- Handling platform-specific behavior (safe areas, keyboard, back button)
- Optimizing list and rendering performance (FlatList/SectionList)
- Managing mobile persistence (AsyncStorage/MMKV) and app lifecycle

## Do not use this skill when

- The project is React web (use `react-pro`)
- The project is Next.js (use `react-next-frontend`)

## Workflow (Deterministic)

1. Confirm runtime (Expo managed vs bare RN), target platforms, and navigation approach.
2. Implement UI with platform-safe primitives and predictable layout.
3. Handle platform-specific behavior explicitly (SafeArea, keyboard, Android back).
4. Treat lists as a performance surface (memoized row, stable keys, FlatList tuning).
5. Validate on both iOS and Android (simulator + at least one real device when possible).

## Output Contract (Always)

- Component changes with platform handling notes
- Navigation integration notes (routes, params, deep links if relevant)
- Performance notes for lists/images
- Verification steps (which devices/platforms and what to test)

## References (Optional)

- Navigation: `references/expo-router.md`
- Platform handling: `references/platform-handling.md`
- List optimization: `references/list-optimization.md`
- Storage hooks: `references/storage-hooks.md`
- Project structure: `references/project-structure.md`
