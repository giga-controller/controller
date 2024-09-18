import { AuthParamProps, integrationEnum } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth-base";
import { capitaliseFirstLetter } from "@/lib/utils";

export default function SlackAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name={capitaliseFirstLetter(integrationEnum.Values.slack)}
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      scope="channels:read,chat:write,users:read"
    />
  );
}
