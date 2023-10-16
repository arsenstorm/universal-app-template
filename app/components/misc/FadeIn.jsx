import { MotiView } from 'moti'

export default function FadeIn({ children }) {
    return (
        <MotiView
            from={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ type: 'timing' }}
        >
            {children}
        </MotiView>
    )
}