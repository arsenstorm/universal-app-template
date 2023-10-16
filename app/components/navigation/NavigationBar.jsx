import React from 'react';
import { Text, TextInput, TouchableOpacity, View, Button } from "react-native";

export default function NavigationBar({ }) {
  // FIXME: height of 24 is good, but this should be done using padding
  return (
    <View className="bg-violet-600 px-2 h-24 border-t-2 border-violet-800">
      <Text
        className="text-base font-bold text-white text-center py-2"
      >
        Navigation Bar
      </Text>
    </View>
  );
}