import React from "react";
import { SafeAreaView, Text, StyleSheet, View, Button } from "react-native";

// Clerk
import { ClerkProvider, SignedIn, SignedOut } from "@clerk/clerk-expo";
import Constants from "expo-constants"

// Auth
import AuthScreen from "./components/auth/AuthScreen";

// Navigation
import NavigationBar from "./components/navigation/NavigationBar";

// Page Components
import Dashboard from "./components/app/Dashboard";

// Secure Token Storage
import * as SecureStore from "expo-secure-store";
import AsyncStorage from '@react-native-async-storage/async-storage';

// Secure Token Cache
const tokenCache = {
  async getToken(key) {
    if (Platform.OS === 'web') {
      try {
        const value = await AsyncStorage.getItem(key);
        if (value !== null) {
          return value;
        }
        return null;
      } catch (e) {
        return null;
      }
    }
    try {
      return SecureStore.getItemAsync(key);
    } catch (err) {
      console.error("here: ", err);
      return null;
    }
  },
  async saveToken(key, value) {
    console.log("Saving token (", key, "):", value);
    if (Platform.OS === 'web') {
      try {
        await AsyncStorage.setItem(key, value);
        return;
      } catch (e) {
        return;
      }
    }
    try {
      return SecureStore.setItemAsync(key, value);
    } catch (err) {
      return;
    }
  },
};

// Animations
import 'react-native-reanimated'
import 'react-native-gesture-handler'

// Animation Fix
import { Platform } from 'react-native'
if (Platform.OS === 'web') {
  global._frameTimestamp = null
}

// Styles
import { NativeWindStyleSheet, styled } from 'nativewind';

// TailwindCSS Bug Fix:
NativeWindStyleSheet.setOutput({
  default: "native",
});

// Heroicons:
import { SparklesIcon } from "react-native-heroicons/solid";

// Icons for Styling:
const StyledSparklesIcon = styled(SparklesIcon);
// As you can see above, you must use the styled() function to style your icons
// This is because it is unsupported by Babel.

export default function App() {
  const [currentPage, setCurrentPage] = React.useState('');

  const currentView = ({ uid = currentPage }) => {
    return {
      '': <Dashboard />,
    }[uid];
  };

  return (
    <ClerkProvider
      tokenCache={tokenCache}
      publishableKey={Constants.expoConfig.extra.clerkPublishableKey}
    >
      <View className="flex-1">
        <SignedIn>
          <View className="flex-1">
            {/* On desktop/web, the navigation bar is fixed to the top of the screen */}
            {Platform.OS === 'web' && (
              <NavigationBar type="desktop" />
            )}
            {currentView(currentPage)}
            {/* On mobile, the navigation bar is fixed to the bottom of the screen */}
            {Platform.OS !== 'web' && (
              <NavigationBar type="mobile" />
            )}
          </View>
        </SignedIn>
        <SignedOut>
          <View className="flex-1 justify-center items-center">
            {/*<View className="mb-64">
              <Loader size={96} duration={1000} reverse />
            </View>
            <StyledSparklesIcon className="w-6 h-6 text-red-500" />*/}
            <AuthScreen />
          </View>
        </SignedOut>
      </View>
    </ClerkProvider>
  );
}
