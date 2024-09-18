import { isUserAuthenticated } from "@/actions/token";
import { INTEGRATION_AUTH_STATUS_QUERY_KEY } from "@/constants/keys";
import { tokenGetRequestSchema } from "@/types/actions/token";
import { Integration, integrationIconMapping } from "@/types/integration";
import { useQuery } from "@tanstack/react-query";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import RoutingAuthDialogContent from "@/components/dialog-content/routing-base";
import { capitaliseFirstLetter } from "@/lib/utils";

type IntegrationIconProps = {
  integration: Integration;
  isHighlighted: boolean;
  apiKey: string;
  clickIntegration: (integration: Integration) => void;
  removeIntegration: (integration: Integration) => void;
};
export default function IntegrationIcon({
  integration,
  isHighlighted,
  apiKey,
  clickIntegration,
  removeIntegration,
}: IntegrationIconProps) {
  const IconComponent = integrationIconMapping[integration];
  const [showAuthRequirementDialog, setShowAuthRequirementDialog] =
    useState<boolean>(false);
  const [showIntegrationAuthDialog, setShowIntegrationAuthDialog] =
    useState<boolean>(false);

  const { data: isAuthenticated, isLoading } = useQuery({
    queryKey: [INTEGRATION_AUTH_STATUS_QUERY_KEY(integration), apiKey],
    queryFn: async () => {
      if (!apiKey) {
        return false;
      }
      const parsedTokenGetRequest = tokenGetRequestSchema.parse({
        api_key: apiKey,
        table_name: integration.toLowerCase(),
      });
      const response = await isUserAuthenticated(parsedTokenGetRequest);
      if (!response.is_authenticated) {
        removeIntegration(integration);
      }
      return response.is_authenticated;
    },
    staleTime: 5 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: false,
  });

  const handleIntegrationClick = (input: Integration) => {
    if (!isAuthenticated) {
      setShowAuthRequirementDialog(true);
      return;
    }
    clickIntegration(input);
  };

  const authRequirementDialog = (
    <Dialog
      open={showAuthRequirementDialog}
      onOpenChange={setShowAuthRequirementDialog}
    >
      <DialogTrigger asChild>
        <Button className="hidden" />
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Authentication Required</DialogTitle>
        <DialogDescription>
          You need to be authenticated to access this integration.
        </DialogDescription>
        <Button
          onClick={() => {
            setShowAuthRequirementDialog(false);
            setShowIntegrationAuthDialog(true);
          }}
        >
          Configure {capitaliseFirstLetter(integration)} Authentication
        </Button>
      </DialogContent>
    </Dialog>
  );

  return (
    <>
      {IconComponent ? (
        <div
          className={`flex items-center justify-end group transition-opacity duration-300 ${isHighlighted ? "opacity-100" : "opacity-30"} ${isLoading ? "pointer-events-none animate-pulse" : ""}`}
          onClick={() => !isLoading && handleIntegrationClick(integration)}
        >
          <p
            className={`group-hover:underline group-hover:text-glow group-hover:cursor-pointer ${isLoading ? "animate-pulse" : ""}`}
          >
            {capitaliseFirstLetter(integration)}
          </p>
          <IconComponent className="m-2 w-8 h-8 group-hover:cursor-pointer" />
        </div>
      ) : null}
      {authRequirementDialog}

      {/* This is tech debt - the format isnt standardised because we are using the integrationAuthDialogContent in original home page in a different form */}
      <Dialog
        open={showIntegrationAuthDialog}
        onOpenChange={setShowIntegrationAuthDialog}
      >
        <DialogContent>
          <RoutingAuthDialogContent apiKey={apiKey} integration={integration} />
        </DialogContent>
      </Dialog>
    </>
  );
}
