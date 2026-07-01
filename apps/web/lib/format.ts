export function formatInrShort(amount: number): string {
  if (amount >= 1_00_00_000) return `₹${(amount / 1_00_00_000).toFixed(2)} Cr`;
  if (amount >= 1_00_000) return `₹${(amount / 1_00_000).toFixed(1)} L`;
  return `₹${amount.toLocaleString("en-IN")}`;
}

export function formatKm(km: number): string {
  return `${km} km/day`;
}

export function confidenceLabel(score: number): { label: string; tone: "emerald" | "amber" | "slate" } {
  if (score >= 70) return { label: "High confidence", tone: "emerald" };
  if (score >= 40) return { label: "Medium confidence", tone: "amber" };
  return { label: "Lower confidence", tone: "slate" };
}

const BODY_TYPE_LABELS: Record<string, string> = {
  hatchback: "Hatchback",
  sedan: "Sedan",
  suv: "SUV",
  muv: "MUV",
  coupe: "Coupe",
  convertible: "Convertible",
  pickup: "Pickup",
};

const FUEL_TYPE_LABELS: Record<string, string> = {
  petrol: "Petrol",
  diesel: "Diesel",
  cng: "CNG",
  electric: "Electric",
  hybrid: "Hybrid",
};

const TRANSMISSION_LABELS: Record<string, string> = {
  manual: "Manual",
  automatic: "Automatic",
  amt: "AMT",
  cvt: "CVT",
  dct: "DCT",
};

export function bodyTypeLabel(value: string): string {
  return BODY_TYPE_LABELS[value] ?? value;
}

export function fuelTypeLabel(value: string): string {
  return FUEL_TYPE_LABELS[value] ?? value;
}

export function transmissionLabel(value: string): string {
  return TRANSMISSION_LABELS[value] ?? value;
}
