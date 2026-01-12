const MovieCardSkeleton = () => {
  return (
    <div className="glass rounded-xl overflow-hidden">
      {/* Poster Skeleton */}
      <div className="aspect-[2/3] animate-shimmer" />
      
      {/* Content Skeleton */}
      <div className="p-4 space-y-3">
        <div className="space-y-2">
          <div className="h-5 w-3/4 rounded animate-shimmer" />
          <div className="h-4 w-1/4 rounded animate-shimmer" />
        </div>
        
        <div className="flex gap-1">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="w-4 h-4 rounded animate-shimmer" />
          ))}
        </div>
        
        <div className="flex gap-2">
          <div className="h-6 w-16 rounded-full animate-shimmer" />
          <div className="h-6 w-20 rounded-full animate-shimmer" />
        </div>
      </div>
    </div>
  );
};

export default MovieCardSkeleton;
