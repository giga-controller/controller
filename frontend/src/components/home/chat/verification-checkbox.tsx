import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

type VerificationCheckboxProps = {
  enableVerification: boolean;
  updateEnableVerification: (input: boolean) => void;
};

export default function VerificationCheckbox({
  enableVerification,
  updateEnableVerification,
}: VerificationCheckboxProps) {
  return (
    <div className="flex space-x-2 bg-white text-black dark:bg-black dark:text-white p-1 rounded">
      <Checkbox
        id="enable-verification"
        checked={enableVerification}
        onCheckedChange={(checked) =>
          updateEnableVerification(checked === true)
        }
      />
      <div className="flex items-center">
        <Label
          htmlFor="enable-verification"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Enable Verification
        </Label>
      </div>
    </div>
  );
}
