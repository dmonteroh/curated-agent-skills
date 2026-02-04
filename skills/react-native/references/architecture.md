# React Native Architecture

Use this for app-level structure and cross-cutting concerns in React Native/Expo apps.

## Project Structure (Expo Router)

```
src/
├── app/                    # Expo Router screens
│   ├── (auth)/            # Auth group
│   ├── (tabs)/            # Tab navigation
│   └── _layout.tsx        # Root layout
├── components/
│   ├── ui/                # Reusable UI components
│   └── features/          # Feature-specific components
├── hooks/                 # Custom hooks
├── services/              # API and native services
├── stores/                # State management
├── utils/                 # Utilities
└── types/                 # TypeScript types
```

## Expo vs Bare React Native

| Feature | Expo | Bare RN |
| --- | --- | --- |
| Setup complexity | Low | High |
| Native modules | EAS Build | Manual linking |
| OTA updates | Built-in | Manual setup |
| Build service | EAS | Custom CI |
| Custom native code | Config plugins | Direct access |

## Auth Flow (Expo Router)

- Use `SecureStore` for tokens.
- Guard routes with `useSegments` and redirect based on auth state.

```tsx
const inAuthGroup = segments[0] === "(auth)";
if (!user && !inAuthGroup) router.replace("/login");
if (user && inAuthGroup) router.replace("/(tabs)");
```

## Offline-First Data (TanStack Query)

- Use `PersistQueryClientProvider` with AsyncStorage.
- Set `networkMode: "offlineFirst"` for queries and mutations.
- Sync `onlineManager` with NetInfo.

## Native Module Integration

- Prefer Expo modules first (`expo-haptics`, `expo-notifications`, `expo-local-authentication`).
- Wrap native modules behind small service functions to isolate platform checks.

## Performance Basics

- Use `FlashList` for long lists.
- Memoize list items and pass primitive props.
- Use `reanimated` for 60fps animations.

## EAS Build & Submit

```json
{
  "build": {
    "development": { "developmentClient": true, "distribution": "internal" },
    "preview": { "distribution": "internal", "android": { "buildType": "apk" } },
    "production": { "autoIncrement": true }
  }
}
```

```bash
# Build
EAS_NO_VCS=1 eas build --platform ios --profile development
EAS_NO_VCS=1 eas build --platform android --profile preview

# Submit
EAS_NO_VCS=1 eas submit --platform ios
EAS_NO_VCS=1 eas submit --platform android
```
