import {
  Building2,
  Car,
  CarFront,
  Caravan,
  Fuel,
  Gauge,
  Leaf,
  Mountain,
  ShieldCheck,
  Sparkles,
  Star,
  Wallet,
  Wind,
  Zap,
} from "lucide-react";

import type {
  BodyTypePreference,
  FuelPreference,
  Priority,
  PrimaryUsage,
  TransmissionPreference,
} from "@/lib/types";

export const USAGE_OPTIONS: { value: PrimaryUsage; label: string; description: string }[] = [
  { value: "city", label: "Mostly city driving", description: "Traffic, short trips, frequent stops" },
  { value: "highway", label: "Mostly highway", description: "Long stretches, higher speeds" },
  { value: "mixed", label: "A mix of both", description: "Some city, some highway" },
];

export const FUEL_OPTIONS: { value: FuelPreference | null; label: string; icon: typeof Fuel }[] = [
  { value: null, label: "No preference", icon: Sparkles },
  { value: "petrol", label: "Petrol", icon: Fuel },
  { value: "diesel", label: "Diesel", icon: Fuel },
  { value: "cng", label: "CNG", icon: Leaf },
  { value: "electric", label: "Electric", icon: Zap },
  { value: "hybrid", label: "Hybrid", icon: Wind },
];

export const TRANSMISSION_OPTIONS: {
  value: TransmissionPreference | null;
  label: string;
}[] = [
  { value: null, label: "No preference" },
  { value: "manual", label: "Manual" },
  { value: "automatic", label: "Automatic" },
  { value: "amt", label: "AMT" },
  { value: "cvt", label: "CVT" },
  { value: "dct", label: "DCT" },
];

export const BODY_TYPE_OPTIONS: { value: BodyTypePreference; label: string; icon: typeof Car }[] = [
  { value: "hatchback", label: "Hatchback", icon: Car },
  { value: "sedan", label: "Sedan", icon: CarFront },
  { value: "suv", label: "SUV", icon: Mountain },
  { value: "muv", label: "MUV", icon: Caravan },
  { value: "coupe", label: "Coupe", icon: Gauge },
  { value: "convertible", label: "Convertible", icon: Sparkles },
  { value: "pickup", label: "Pickup", icon: Building2 },
];

export const PRIORITY_OPTIONS: { value: Priority; label: string; icon: typeof Star }[] = [
  { value: "fuel_economy", label: "Fuel economy", icon: Leaf },
  { value: "safety", label: "Safety", icon: ShieldCheck },
  { value: "comfort_features", label: "Comfort & features", icon: Sparkles },
  { value: "performance", label: "Performance", icon: Gauge },
  { value: "low_price", label: "Low price", icon: Wallet },
  { value: "reliability_brand_trust", label: "Reliability & brand trust", icon: Star },
];
