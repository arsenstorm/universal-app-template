import React, { createContext, useContext, useState } from "react";
import { Text, TextInput, TouchableOpacity, View } from "react-native";

// Styles
import { NativeWindStyleSheet } from 'nativewind';

NativeWindStyleSheet.setOutput({
    default: "native",
});

/*function SignInScreen() {
    const { signIn, setActive, isLoaded } = useSignIn();

    const [emailAddress, setEmailAddress] = React.useState("");
    const [password, setPassword] = React.useState("");

    const onSignInPress = async () => {
        if (!isLoaded) {
            return;
        }

        try {
            const completeSignIn = await signIn.create({
                identifier: emailAddress,
                password,
            });
            // This is an important step,
            // This indicates the user is signed in
            await setActive({ session: completeSignIn.createdSessionId });
        } catch (err) {
            console.log(err);
        }
    };
    return (
        <View className="bg-white border border-stone-200 rounded-2xl p-4 max-w-md w-full mx-auto">
            <View>
                <TextInput
                    autoCapitalize="none"
                    value={emailAddress}
                    placeholder="Email..."
                    className="bg-white text-black p-4 border-2 border-stone-300 rounded-full m-4"
                    onChangeText={(emailAddress) => setEmailAddress(emailAddress)}
                />
            </View>

            <View>
                <TextInput
                    value={password}
                    placeholder="Password..."
                    secureTextEntry={true}
                    className="bg-white text-black p-4 border-2 border-stone-300 rounded-full m-4"
                    onChangeText={(password) => setPassword(password)}
                />
            </View>

            <TouchableOpacity
                onPress={onSignInPress}
                className="bg-violet-900 p-4 rounded-full m-4"
            >
                <Text
                    className="text-white text-center"
                >Sign in</Text>
            </TouchableOpacity>
        </View>
    );
}

function SignUpScreen() {
    const { isLoaded, signUp, setActive } = useSignUp();

    const [emailAddress, setEmailAddress] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [pendingVerification, setPendingVerification] = React.useState(false);
    const [code, setCode] = React.useState("");

    // start the sign up process.
    const onSignUpPress = async () => {
        if (!isLoaded) {
            return;
        }

        try {
            await signUp.create({
                emailAddress,
                password,
            });

            // send the email.
            await signUp.prepareEmailAddressVerification({ strategy: "email_code" });

            // change the UI to our pending section.
            setPendingVerification(true);
        } catch (err) {
            console.error(JSON.stringify(err, null, 2));
        }
    };

    // This verifies the user using email code that is delivered.
    const onPressVerify = async () => {
        if (!isLoaded) {
            return;
        }

        try {
            const completeSignUp = await signUp.attemptEmailAddressVerification({
                code,
            });

            await setActive({ session: completeSignUp.createdSessionId });
        } catch (err) {
            console.error(JSON.stringify(err, null, 2));
        }
    };

    return (
        <View className="bg-white border border-stone-200 rounded-2xl p-4 max-w-md w-full mx-auto">
            {!pendingVerification && (
                <View>
                    <View>
                        <TextInput
                            autoCapitalize="none"
                            value={emailAddress}
                            placeholder="Email..."
                            className="bg-white text-black p-4 border-2 border-stone-300 rounded-full m-4"
                            onChangeText={(email) => setEmailAddress(email)}
                        />
                    </View>

                    <View>
                        <TextInput
                            value={password}
                            placeholder="Password..."
                            className="bg-white text-black p-4 border-2 border-stone-300 rounded-full m-4"
                            secureTextEntry={true}
                            onChangeText={(password) => setPassword(password)}
                        />
                    </View>

                    <TouchableOpacity
                        onPress={onSignUpPress}
                        className="bg-violet-900 p-4 rounded-full m-4"
                    >
                        <Text
                            className="text-white text-center"
                        >
                            Sign up
                        </Text>
                    </TouchableOpacity>
                </View>
            )}
            {pendingVerification && (
                <View>
                    <View>
                        <TextInput
                            value={code}
                            placeholder="Code..."
                            className="bg-white text-black p-4 border-2 border-stone-300 rounded-full m-4"
                            onChangeText={(code) => setCode(code)}
                        />
                    </View>
                    <TouchableOpacity
                        onPress={onPressVerify}
                        className="bg-violet-900 p-4 rounded-full m-4"
                    >
                        <Text
                            className="text-white text-center"
                        >
                            Verify Email
                        </Text>
                    </TouchableOpacity>
                </View>
            )}
        </View>
    );
}*/

const AuthScreenContext = createContext();

function AuthScreen() {
    return (
        <>
            This is deployed on Cloudflare
        </>
    );
    const [screen, setScreen] = useState('signin'); // 'signin' or 'signup'

    const toggleScreen = () => {
        setScreen((prevScreen) => (prevScreen === 'signin' ? 'signup' : 'signin'));
    };

    return (
        <AuthScreenContext.Provider value={{ toggleScreen }}>
            <View className="bg-white border border-stone-200 rounded-2xl p-4 max-w-md w-full mx-auto">
                {screen === 'signin' && <SignInScreen />}
                {screen === 'signup' && <SignUpScreen />}
                <View className="bg-white border border-stone-200 rounded-2xl p-4 max-w-md w-full mx-auto mt-4">
                    <TouchableOpacity onPress={toggleScreen} className="">
                        <Text className="text-black text-center">
                            {screen === 'signin' ? 'Sign Up Instead' : 'Sign In Instead'}
                        </Text>
                        {screen === 'signin' ? (
                            <>
                            </>
                        ) : (
                            <Text className="text-black text-center">
                                Forgot Password?
                            </Text>
                        )}
                    </TouchableOpacity>
                </View>
            </View>
        </AuthScreenContext.Provider>
    );
}

// Original SignInScreen & SignUpScreen Components can stay the same.

function useAuthScreen() {
    const context = useContext(AuthScreenContext);
    if (!context) {
        throw new Error('useAuthScreen must be used within an AuthScreenProvider');
    }
    return context;
}

export { AuthScreen, useAuthScreen };