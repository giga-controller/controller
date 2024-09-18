import { Integration, integrationEnum } from "@/types/integration";
import GmailAuthDialogContent from "@/components/dialog-content/gmail";
import GoogleCalendarAuthDialogContent from "@/components/dialog-content/calendar";
import LinearAuthDialogContent from "@/components/dialog-content/linear";
import SlackAuthDialogContent from "@/components/dialog-content/slack";
import XAuthDialogContent from "@/components/dialog-content/x";
import GoogleSheetsAuthDialogContent from "@/components/dialog-content/sheets";

type RoutingAuthDialogContentProps = {
  apiKey: string;
  integration: Integration;
};

export default function RoutingAuthDialogContent({
  apiKey,
  integration,
}: RoutingAuthDialogContentProps) {
  let dialogContent = null;
  switch (integration) {
    case integrationEnum.Values.gmail:
      dialogContent = (
        <GmailAuthDialogContent
          apiKey={apiKey}
          loginBase="https://accounts.google.com/o/oauth2/v2/auth"
          exchangeBase="https://oauth2.googleapis.com/token"
        />
      );
      break;
    case integrationEnum.Values.linear:
      dialogContent = (
        <LinearAuthDialogContent
          apiKey={apiKey}
          loginBase="https://linear.app/oauth/authorize"
          exchangeBase="https://api.linear.app/oauth/token"
        />
      );
      break;
    case integrationEnum.Values.slack:
      dialogContent = (
        <SlackAuthDialogContent
          apiKey={apiKey}
          loginBase="https://slack.com/oauth/v2/authorize"
          exchangeBase="https://slack.com/api/oauth.v2.access"
        />
      );
      break;
    case integrationEnum.Values.x:
      dialogContent = (
        <XAuthDialogContent
          apiKey={apiKey}
          loginBase="https://twitter.com/i/oauth2/authorize"
          exchangeBase="https://api.x.com/2/oauth2/token"
        />
      );
      break;
    case integrationEnum.Values.calendar:
      dialogContent = (
        <GoogleCalendarAuthDialogContent
          apiKey={apiKey}
          loginBase="https://accounts.google.com/o/oauth2/v2/auth"
          exchangeBase="https://oauth2.googleapis.com/token"
        />
      );
      break;
    case integrationEnum.Values.sheets:
      dialogContent = (
        <GoogleSheetsAuthDialogContent
          apiKey={apiKey}
          loginBase="https://accounts.google.com/o/oauth2/v2/auth"
          exchangeBase="https://oauth2.googleapis.com/token"
        />
      );
      break;
  }
  return dialogContent;
}
