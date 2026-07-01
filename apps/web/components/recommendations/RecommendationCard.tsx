import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  Cog,
  Fuel,
  Gauge,
  MessageSquareText,
  Package,
  Sparkles,
  Users,
} from "lucide-react";

import { Badge } from "@/components/ui/Badge";
import { StarRating } from "@/components/ui/StarRating";
import {
  bodyTypeLabel,
  confidenceLabel,
  formatInrShort,
  fuelTypeLabel,
  transmissionLabel,
} from "@/lib/format";
import type { CarRecommendationResult } from "@/lib/types";

function scoreTone(score: number): string {
  if (score >= 80) return "text-emerald-600";
  if (score >= 60) return "text-indigo-600";
  if (score >= 40) return "text-amber-600";
  return "text-slate-500";
}

// The backend's honest fallback when no dimension scored below the candidate median --
// good news, so it shouldn't render under the same warning icon as a real trade-off.
function hasNoRealTradeOffs(tradeOffs: string[]): boolean {
  return tradeOffs.length === 1 && tradeOffs[0].includes("No significant compromises");
}

export function RecommendationCard({
  result,
  rank,
}: {
  result: CarRecommendationResult;
  rank: number;
}) {
  const confidence = confidenceLabel(result.score_confidence);

  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
      <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Badge tone="indigo">{rank === 1 ? "Best match" : `#${rank} match`}</Badge>
          <h2 className="mt-3 text-xl font-semibold text-slate-900">
            {result.maker_name} {result.model_name}
          </h2>
          <p className="text-slate-500">{result.variant_name}</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">
            {formatInrShort(result.price)}
          </p>
        </div>
        <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
          <div className={`text-3xl font-bold ${scoreTone(result.overall_score)}`}>
            {Math.round(result.overall_score)}
            <span className="text-base font-medium text-slate-400">/100</span>
          </div>
          <Badge tone={confidence.tone}>{confidence.label}</Badge>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-3 rounded-2xl bg-slate-50 p-4 text-sm sm:grid-cols-4">
        <SpecItem icon={Fuel} label={fuelTypeLabel(result.fuel_type)} />
        <SpecItem icon={Cog} label={transmissionLabel(result.transmission_type)} />
        <SpecItem icon={Users} label={result.seating_capacity ? `${result.seating_capacity} seats` : "—"} />
        <SpecItem
          icon={Gauge}
          label={result.mileage_kmpl ? `${result.mileage_kmpl.toFixed(1)} kmpl` : "—"}
        />
        <SpecItem icon={Package} label={bodyTypeLabel(result.body_type)} />
        <SpecItem icon={Sparkles} label={result.power_bhp ? `${Math.round(result.power_bhp)} bhp` : "—"} />
      </div>

      {result.match_reasons.length > 0 && (
        <ReasonList
          icon={CheckCircle2}
          iconClassName="text-emerald-600"
          title="Why this fits you"
          items={result.match_reasons}
        />
      )}

      {result.trade_offs.length > 0 &&
        (hasNoRealTradeOffs(result.trade_offs) ? (
          <ReasonList
            icon={CheckCircle2}
            iconClassName="text-emerald-600"
            title="Worth knowing"
            items={result.trade_offs}
          />
        ) : (
          <ReasonList
            icon={AlertTriangle}
            iconClassName="text-amber-600"
            title="Worth knowing"
            items={result.trade_offs}
          />
        ))}

      {result.key_feature_highlights.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-slate-700">Key features</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {result.key_feature_highlights.map((feature) => (
              <Badge key={feature} tone="slate">
                {feature}
              </Badge>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 border-t border-slate-100 pt-5">
        <div className="flex items-center gap-3">
          {result.reviews.average_rating !== null ? (
            <>
              <StarRating rating={result.reviews.average_rating} />
              <span className="text-sm font-medium text-slate-700">
                {result.reviews.average_rating.toFixed(1)}
              </span>
              <span className="text-sm text-slate-400">
                ({result.reviews.review_count} review{result.reviews.review_count === 1 ? "" : "s"})
              </span>
            </>
          ) : (
            <span className="text-sm text-slate-400">No reviews yet</span>
          )}
        </div>

        {result.reviews.snippets.length > 0 && (
          <details className="group mt-3">
            <summary className="flex cursor-pointer list-none items-center gap-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-700">
              <MessageSquareText className="h-4 w-4" />
              Read reviews
              <ChevronDown className="h-4 w-4 transition-transform group-open:rotate-180" />
            </summary>
            <ul className="mt-3 space-y-3">
              {result.reviews.snippets.map((snippet, index) => (
                <li key={index} className="rounded-xl bg-slate-50 p-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-700">{snippet.reviewer_name}</span>
                    <StarRating rating={snippet.rating} />
                  </div>
                  {snippet.comment && <p className="mt-1 text-slate-600">{snippet.comment}</p>}
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>
    </article>
  );
}

function SpecItem({ icon: Icon, label }: { icon: typeof Fuel; label: string }) {
  return (
    <div className="flex items-center gap-2 text-slate-600">
      <Icon className="h-4 w-4 shrink-0 text-slate-400" />
      <span className="truncate">{label}</span>
    </div>
  );
}

function ReasonList({
  icon: Icon,
  iconClassName,
  title,
  items,
}: {
  icon: typeof CheckCircle2;
  iconClassName: string;
  title: string;
  items: string[];
}) {
  return (
    <div className="mt-6">
      <h3 className="text-sm font-semibold text-slate-700">{title}</h3>
      <ul className="mt-2 space-y-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-2 text-sm text-slate-600">
            <Icon className={`h-4 w-4 shrink-0 mt-0.5 ${iconClassName}`} />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
