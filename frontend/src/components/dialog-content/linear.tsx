import { AuthParamProps, integrationEnum } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth-base";
import { capitaliseFirstLetter } from "@/lib/utils";

export default function LinearAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name={capitaliseFirstLetter(integrationEnum.Values.linear)}
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      // scope="read,write,issues:create,comments:create,timeSchedule:write" // Full available scope, but timeSchedule:write bugs out oauth 2 token change for some reason
      scope="read,write,issues:create,comments:create"
      verifierRequired={false}
    />
  );
}
