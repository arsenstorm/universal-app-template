import React from 'react';
import { Text, TextInput, TouchableOpacity, View, Button, SafeAreaView } from "react-native";
import { SparklesIcon } from "react-native-heroicons/solid";
import FadeIn from '../misc/FadeIn';
import { MotiView } from 'moti';
import { Skeleton } from 'moti/skeleton';

export default function Dashboard({ }) {
  return (
    <SafeAreaView className="bg-white flex-1 w-full p-16">
      <View className="px-4">
        <MotiView
          transition={{
            type: 'timing',
          }}
          animate={{ backgroundColor: '#ffffff' }}
        >
          <Skeleton colorMode={'light'} radius="round" height={75} width={75} />
          <Spacer />
          <Skeleton colorMode={'light'} width={'100%'} />
          <Spacer height={8} />
          <Skeleton colorMode={'light'} width={'100%'} />
          <Spacer height={8} />
          <Skeleton colorMode={'light'} width={'100%'} />
        </MotiView>
      </View>
    </SafeAreaView>
  );
}

const Spacer = ({ height = 16 }) => <View style={{ height }} />;