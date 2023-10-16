import React from 'react';
import { View, Text } from 'react-native';
import { MotiView } from 'moti';

export default function Spin({ duration = 1000, reverse = false, children }) {
    return (
        <View style={{ alignItems: 'center', justifyContent: 'center' }}>
            <MotiView
                from={{ rotate: '0deg' }}
                animate={{ rotate: '360deg' }}
                transition={{
                    loop: true,
                    repeatReverse: reverse,
                    type: 'timing',
                    duration: duration,
                }}
                style={{ position: 'absolute' }}
            >
                {children}
            </MotiView>
        </View>
    );
}
