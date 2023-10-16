import React from 'react';
import { Text, TextInput, TouchableOpacity, View, Button, SafeAreaView } from "react-native";
import {
    ArrowPathIcon
} from "react-native-heroicons/solid";
import Spin from './Spin';

export default function Loader({ size = 50, color = "#4c1d95", duration = 1000, reverse = false }) {
    return (
        <SafeAreaView>
            <Spin duration={duration} reverse={reverse}>
                <ArrowPathIcon
                    size={size}
                    color={color}
                />
            </Spin>
        </SafeAreaView>
    )
}