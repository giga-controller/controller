import { Button } from "@/components/ui/button";
import { userVerificationSchema } from "@/types/actions/query/confirm";

type VerificationOptionProps = {
    isEnabled: boolean;
    sendMessage: (input: string) => void;
}

export default function VerificationOption({ isEnabled, sendMessage }: VerificationOptionProps) {
    if (!isEnabled) {
        return null;
    }
    
    return (
        <div className="absolute inset-0 flex items-center justify-center space-x-4">
            <Button
            onClick={() => sendMessage(userVerificationSchema.Values.YES)}
            >
            YES
            </Button>
            <Button onClick={() => sendMessage(userVerificationSchema.Values.NO)}>
            NO
            </Button>
        </div>
    )
}