import { AuthParamProps, integrationEnum } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth-base";
import { capitaliseFirstLetter } from "@/lib/utils";

export default function GmailAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name={capitaliseFirstLetter(integrationEnum.Values.gmail)}
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      scope="https://mail.google.com/"
    />
  );
}
