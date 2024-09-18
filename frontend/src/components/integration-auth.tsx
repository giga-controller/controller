"use client";

import { Integration, integrationIconMapping } from "@/types/integration";
import { CiFaceSmile } from "react-icons/ci";
import { IconType } from "react-icons/lib";
import { useState } from "react";
import {
  Dialog,
  DialogContent as DialogContentWrapper,
  DialogTrigger,
} from "@/components/ui/dialog";
import RoutingAuthDialogContent from "@/components/dialog-content/routing-base";

type CardProps = {
  integration: Integration;
  apiKey: string;
};

export default function IntegrationAuth({ integration, apiKey }: CardProps) {
  const DEFAULT_ICON: IconType = CiFaceSmile;

  const IconComponent = integrationIconMapping[integration] || DEFAULT_ICON;

  const [isHovered, setIsHovered] = useState<boolean>(false);

  return (
    <Dialog>
      <DialogTrigger>
        <div className="flex flex-col items-center justify-center">
          <div
            className={`cursor-pointer transition-colors duration-300 ${isHovered ? "text-primary" : "text-muted-foreground"}`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            <IconComponent size={80} />
          </div>
          <h2 className="mt-2 text-lg font-semibold transition-opacity duration-1000 opacity-100">
            {integration}
          </h2>
        </div>
      </DialogTrigger>
      <DialogContentWrapper>
        <RoutingAuthDialogContent apiKey={apiKey} integration={integration} />
      </DialogContentWrapper>
    </Dialog>
  );
}
