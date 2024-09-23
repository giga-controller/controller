import { z } from "zod";
import { IconType } from "react-icons/lib";
import { BiLogoGmail } from "react-icons/bi";
import {
  SiGooglecalendar,
  SiSlack,
  SiLinear,
  SiMicrosoftoutlook,
  SiGooglesheets,
  SiGoogledocs,
} from "react-icons/si";
import { FaXTwitter } from "react-icons/fa6";

export const integrationEnum = z.enum([
  "calendar",
  "docs",
  "gmail",
  "linear",
  "outlook",
  "sheets",
  "slack",
  "x",
]);
export type Integration = z.infer<typeof integrationEnum>;
export const integrationsStateSchema = z.object({
  integrations: z.array(integrationEnum),
});
export type IntegrationsState = z.infer<typeof integrationsStateSchema>;
export const defaultIntegrationsState: IntegrationsState = {
  integrations: [],
};

const integrationIconMappingSchema = z.record(
  integrationEnum,
  z.custom<IconType>(),
);
type IntegrationIconMapping = z.infer<typeof integrationIconMappingSchema>;

export const integrationIconMapping: IntegrationIconMapping = {
  calendar: SiGooglecalendar,
  docs: SiGoogledocs,
  gmail: BiLogoGmail,
  linear: SiLinear,
  sheets: SiGooglesheets,
  slack: SiSlack,
  outlook: SiMicrosoftoutlook,
  x: FaXTwitter,
};

export type AuthParamProps = {
  apiKey: string;
  loginBase: string;
  exchangeBase: string;
};
