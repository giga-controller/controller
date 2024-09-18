import { AuthParamProps, integrationEnum } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth-base";
import { capitaliseFirstLetter } from "@/lib/utils";

export default function XAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name={capitaliseFirstLetter(integrationEnum.Values.x)}
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      scope="tweet.read tweet.write users.read follows.read follows.write offline.access"
    />
  );
}
