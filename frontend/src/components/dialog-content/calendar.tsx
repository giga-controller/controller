import { AuthParamProps, integrationEnum } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth-base";
import { capitaliseFirstLetter } from "@/lib/utils";

export default function GoogleCalendarAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name={capitaliseFirstLetter(integrationEnum.Values.calendar)}
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      scope="https://www.googleapis.com/auth/calendar"
    />
  );
}
