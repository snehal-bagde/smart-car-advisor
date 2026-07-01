import { Star } from "lucide-react";

export function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5" aria-label={`${rating} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((position) => (
        <Star
          key={position}
          className="h-4 w-4"
          fill={position <= Math.round(rating) ? "#f59e0b" : "none"}
          stroke={position <= Math.round(rating) ? "#f59e0b" : "#cbd5e1"}
        />
      ))}
    </div>
  );
}
